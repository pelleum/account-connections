from datetime import datetime
from typing import Any, List, Mapping, Union

from fastapi import APIRouter, Body, Depends, Path
from pydantic import constr

from app.dependencies import (
    get_current_active_user,
    get_institution_repo,
    get_institution_service,
    get_portfolio_repo,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.repos.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.schemas import institutions, portfolios, robinhood, users

institution_router = APIRouter(tags=["Institutions"])


@institution_router.get(
    "",
    status_code=200,
    response_model=institutions.SupportedInstitutionsResponse,
)
async def get_all_supported_institutions(
    institution_repo: IInstitutionRepo = Depends(get_institution_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> institutions.SupportedInstitutionsResponse:
    """Retrieve all Pelleum supported institutions"""

    supported_institutions: List[
        institutions.Institution
    ] = await institution_repo.retrieve_all_institutions()

    return institutions.SupportedInstitutionsResponse(
        records=institutions.SupportedInstitutions(
            supported_institutions=supported_institutions
        )
    )


@institution_router.get(
    "/connections",
    status_code=200,
    response_model=institutions.UserActiveConnectionsResponse,
)
async def retrieve_active_institution_connections(
    institution_repo: IInstitutionRepo = Depends(get_institution_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> institutions.UserActiveConnectionsResponse:
    """Retrieve a user's connected accounts"""

    user_active_connections = (
        await institution_repo.retrieve_many_institution_connections(
            query_params=institutions.RetrieveManyConnectionsRepoAdapter(
                user_id=authorized_user.user_id
            )
        )
    )

    active_connections = [
        institutions.ConnectionInResponse(**active_connection.dict())
        for active_connection in user_active_connections
    ]

    return institutions.UserActiveConnectionsResponse(
        records=institutions.UserActiveConnections(
            active_connections=active_connections
        )
    )


@institution_router.delete(
    "/{institution_id}",
    status_code=204,
    response_model=None,
)
async def deactivate_institution_connection(
    institution_id: constr(max_length=100) = Path(...),
    institution_repo: IInstitutionRepo = Depends(get_institution_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:
    """Deactivate a user's connected account"""

    active_connection: institutions.InstitutionConnection = (
        await institution_repo.retrieve_institution_connection(
            user_id=authorized_user.user_id,
            institution_id=institution_id,
            is_active=True,
        )
    )

    if not active_connection:
        raise await pelleum_errors.PelleumErrors(
            detail=f"There is no active connection associated with user_id, {authorized_user.user_id}, and institution_id, {institution_id}."
        ).resource_not_found()

    await institution_repo.update_institution_connection(
        connection_id=active_connection.connection_id,
        updated_connection=institutions.UpdateConnectionRepoAdapter(is_active=False),
    )


@institution_router.post(
    "/login/{institution_id}",
    status_code=200,
    response_model=Union[Mapping[str, Any], institutions.SuccessfulConnectionResponse],
)
async def login_to_institution(
    institution_id: constr(max_length=100) = Path(...),
    body: institutions.LoginRequest = Body(...),
    institution_service: IInstitutionService = Depends(get_institution_service),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> Union[Mapping[str, Any], institutions.SuccessfulConnectionResponse]:
    """Login to institution"""

    try:
        response = await institution_service.login(
            credentials=body,
            user_id=authorized_user.user_id,
            institution_id=institution_id,
        )
    except (
        institutions.InstitutionApiError,
        institutions.InstitutionException,
    ) as error:
        error = (
            error.detail
            if isinstance(error, institutions.InstitutionApiError)
            else str(error)
        )
        raise await pelleum_errors.ExternalError(
            detail=f"Robinhood API Error: {error}"
        ).robinhood()

    if not response:
        return institutions.SuccessfulConnectionResponse(
            account_connection_status="connected", connected_at=datetime.utcnow()
        )
    return response

        
@institution_router.post(
    "/login/{institution_id}/verify",
    status_code=201,
    response_model=institutions.SuccessfulConnectionResponse,
)
async def verify_login_with_code(
    institution_id: constr(max_length=100) = Path(...),
    body: institutions.MultiFactorAuthCodeRequest = Body(...),
    institution_service: IInstitutionService = Depends(get_institution_service),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> institutions.SuccessfulConnectionResponse:
    """Verify login to institution with verifaction code"""

    if not body.sms_code and not body.challenge_id:
        raise pelleum_errors.PelleumErrors(
            detail="Must send either sms_code or challenge_id to this endpoint."
        ).general_bad_request()

    try:
        await institution_service.send_multifactor_auth_code(
            verification_proof=body,
            user_id=authorized_user.user_id,
            institution_id=institution_id,
        )
    except (
        institutions.InstitutionApiError,
        institutions.InstitutionException,
    ) as error:
        error = (
            error.detail
            if isinstance(error, institutions.InstitutionApiError)
            else str(error)
        )
        raise await pelleum_errors.ExternalError(
            detail=f"Robinhood API Error: {error}"
        ).robinhood()

    return institutions.SuccessfulConnectionResponse(
        account_connection_status="connected", connected_at=datetime.utcnow()
    )
