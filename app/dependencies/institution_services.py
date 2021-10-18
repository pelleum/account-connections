from fastapi import Path, Depends
from pydantic import constr
import aiohttp

from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.schemas import institutions
from app.usecases.services.robinhood import RobinhoodService
from app.infrastructure.clients.robinhood import RobinhoodClient
from app.dependencies import get_institution_repo, get_client_session
from app.libraries import pelleum_errors


async def get_institution_service(
    institution_id: constr(max_length=100) = Path(...),
    client_session: aiohttp.client.ClientSession = Depends(get_client_session),
    institution_repo: IInstitutionRepo = Depends(get_institution_repo),
) -> IInstitutionService:

    institution: institutions.Institution = await institution_repo.retrieve_institution(
        institution_id=institution_id
    )

    if not institution:
        raise await pelleum_errors.PelleumErrors(
            detail="Invalid institution_id."
        ).invalid_resource_id()

    if institution.name == "Robinhood":
        return RobinhoodService(
            robinhood_client=RobinhoodClient(client_session=client_session),
            institution_repo=institution_repo,
        )
