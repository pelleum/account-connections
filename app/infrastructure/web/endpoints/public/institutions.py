from datetime import datetime
from typing import List, Mapping, Union

from fastapi import APIRouter, Body, Depends, Path
from pydantic import constr

from app.dependencies import (
    get_current_active_user,
    get_institution_repo,
    get_institution_service,
    get_portfolio_repo,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.clients.robinhood import (
    RobinhoodApiError,
    RobinhoodException,
)
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
            user_id=authorized_user.user_id, is_active=True
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
    response_model=Mapping,
)
async def login_to_institution(
    institution_id: constr(max_length=100) = Path(...),
    body: institutions.LoginRequest = Body(...),
    portfolio_repo: IPortfolioRepo = Depends(get_portfolio_repo),
    institution_service: IInstitutionService = Depends(get_institution_service),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> Union[Mapping, institutions.SuccessfulConnectionResponse]:
    """Login to institution"""

    try:
        response: Union[
            Mapping, robinhood.CreateOrUpdateAssetsOnLogin
        ] = await institution_service.login(
            credentials=body,
            user_id=authorized_user.user_id,
            institution_id=institution_id,
        )
    except RobinhoodApiError as error:
        raise await pelleum_errors.ExternalError(
            detail=f"Robinhood API Error: {error.detail}"
        ).robinhood()
    except RobinhoodException as error:
        raise await pelleum_errors.ExternalError(
            detail=f"Robinhood API Error: {str(error)}"
        ).robinhood()

    if isinstance(response, robinhood.CreateOrUpdateAssetsOnLogin):
        if response.action == "create":
            for asset in response.brokerage_portfolio.holdings:
                await portfolio_repo.create_asset(
                    new_asset=portfolios.CreateAssetRepoAdapter(
                        average_buy_price=asset.average_buy_price
                        if asset.average_buy_price
                        else None,
                        user_id=authorized_user.user_id,
                        institution_id=institution_id,
                        name=asset.asset_name,
                        asset_symbol=asset.asset_symbol,
                        quantity=asset.quantity,
                    )
                )
        elif response.action == "update":
            for asset in response.brokerage_portfolio.holdings:
                await portfolio_repo.update_asset(
                    user_id=authorized_user.user_id,
                    asset_symbol=asset.asset_symbol,
                    institution_id=institution_id,
                    updated_asset=portfolios.UpdateAssetRepoAdapter(
                        is_up_to_date=True,
                        quantity=asset.quantity,
                        average_buy_price=asset.average_buy_price,
                    ),
                )

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
    portfolio_repo: IPortfolioRepo = Depends(get_portfolio_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> institutions.SuccessfulConnectionResponse:
    """Verify login to institution with verifaction code"""

    if not body.sms_code and not body.challenge_id:
        raise pelleum_errors.PelleumErrors(
            detail="Must send either sms_code or challenge_id to this endpoint."
        ).general_bad_request()

    try:
        brokerage_portfolio: institutions.UserHoldings = (
            await institution_service.send_multifactor_auth_code(
                verification_proof=body,
                user_id=authorized_user.user_id,
                institution_id=institution_id,
            )
        )
    except RobinhoodApiError as error:
        raise await pelleum_errors.ExternalError(
            detail=f"Robinhood API Error: {error.detail}"
        ).robinhood()
    except RobinhoodException as error:
        raise await pelleum_errors.ExternalError(
            detail=f"Robinhood API Error: {str(error)}"
        ).robinhood()

    for asset in brokerage_portfolio.holdings:
        await portfolio_repo.create_asset(
            new_asset=portfolios.CreateAssetRepoAdapter(
                average_buy_price=asset.average_buy_price
                if asset.average_buy_price
                else None,
                user_id=authorized_user.user_id,
                institution_id=institution_id,
                name=asset.asset_name,
                asset_symbol=asset.asset_symbol,
                quantity=asset.quantity,
            )
        )

    return institutions.SuccessfulConnectionResponse(
        account_connection_status="connected", connected_at=datetime.utcnow()
    )
