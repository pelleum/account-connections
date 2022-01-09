from typing import List

import aiohttp
from fastapi import Depends, Path
from pydantic import constr

from app.dependencies import get_client_session, get_institution_repo
from app.infrastructure.clients.robinhood import RobinhoodClient
from app.libraries import pelleum_errors
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.interfaces.services.institution_service import IInstitutionService
from app.usecases.schemas import institutions
from app.usecases.services.encryption import EncryptionService
from app.usecases.services.robinhood import RobinhoodService


async def get_institution_service(
    institution_id: constr(max_length=100) = Path(...),
    client_session: aiohttp.client.ClientSession = Depends(get_client_session),
    institution_repo: IInstitutionRepo = Depends(get_institution_repo),
) -> IInstitutionService:
    """Return institution service based on institution_id"""

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
            encryption_service=EncryptionService(),
        )


async def get_all_institution_services() -> List[IInstitutionService]:
    """Return a list of all institution services"""

    client_session: aiohttp.client.ClientSession = await get_client_session()
    institution_repo: IInstitutionRepo = await get_institution_repo()

    robinhood_service = RobinhoodService(
        robinhood_client=RobinhoodClient(client_session=client_session),
        institution_repo=institution_repo,
        encryption_service=EncryptionService(),
    )

    return [robinhood_service]
