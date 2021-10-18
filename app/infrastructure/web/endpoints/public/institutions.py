from typing import List, Mapping
from datetime import datetime

from fastapi import APIRouter, Depends, Body, Path
from pydantic import constr
from app.libraries import pelleum_errors
from app.usecases.interfaces.clients.robinhood import (
    RobinhoodApiError,
    RobinhoodException,
)

from app.usecases.schemas import institutions
from app.usecases.schemas import users
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.dependencies import (
    get_current_active_user,
    get_institution_repo,
    get_institution_service,
)


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

    supported_institutions: List[
        institutions.Institution
    ] = await institution_repo.retrieve_all_institutions()

    return institutions.SupportedInstitutionsResponse(
        records=institutions.SupportedInstitutions(
            supported_institutions=supported_institutions
        )
    )


@institution_router.post(
    "/login/{institution_id}",
    status_code=200,
    response_model=Mapping,
)
async def login_to_institution(
    body: institutions.LoginRequest = Body(...),
    institution_service: IInstitutionService = Depends(get_institution_service),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> Mapping:

    return await institution_service.login(credentials=body)


@institution_router.post(
    "/login/{institution_id}/mfa",
    status_code=201,
    response_model=None,
)
async def send_mfa_code(
    institution_id: constr(max_length=100) = Path(...),
    body: institutions.MultiFactorAuthCodeRequest = Body(...),
    institution_service: IInstitutionService = Depends(get_institution_service),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    try:
        await institution_service.send_multifactor_auth_code(
            credentials=body,
            user_id=authorized_user.user_id,
            institution_id=institution_id,
        )
    except RobinhoodApiError as error:
        raise await pelleum_errors.ExternalError(
            detail=f"Robinhood API Error: {error.detail}"
        ).robinhood()

    return institutions.SuccessfulConnectionResponse(
        account_connection_status="connected", connected_at=datetime.utcnow()
    )
