from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas import institutions


class IInstitutionRepo(ABC):
    @abstractmethod
    async def create(
        self, connection_data: institutions.CreateConnectionRepoAdapter
    ) -> institutions.InstitutionConnection:
        """Creates connection data"""

    @abstractmethod
    async def retrieve_institution(
        self, name: str = None, institution_id: str = None
    ) -> Optional[institutions.InstitutionConnection]:
        """Retrieve single Pelleum supported instution"""

    @abstractmethod
    async def retrieve_all_institutions(self) -> List[institutions.Institution]:
        """Retrieve all Pelleum supported institutions"""

    @abstractmethod
    async def retrieve_institution_connection(
        self, user_id: str = None, institution_id: str = None, is_active: bool = None
    ) -> Optional[institutions.InstitutionConnection]:
        """Retrieve signle user-institution connection"""

    @abstractmethod
    async def update_institution_connection(
        self,
        connection_id: int,
        updated_connection: institutions.UpdateConnectionRepoAdapter,
    ) -> institutions.InstitutionConnection:
        """Update a signle user-institution connection by connection_id"""

    @abstractmethod
    async def retrieve_many_institution_connections(  # pylint: disable=too-many-arguments
        self,
        user_id: int = None,
        institution_id: int = None,
        is_active: bool = None,
        page_number: int = 1,
        page_size: int = 10000,
    ) -> List[institutions.InstitutionConnection]:
        """Retrieve many institution connections"""

    @abstractmethod
    async def create_robinhood_instrument(
        self, instrument_id: str, name: str, symbol: str
    ) -> None:
        """Creates Robinhood instrument in our DB for future reference"""

    @abstractmethod
    async def retrieve_robinhood_instruments(
        self, instrument_ids: list
    ) -> List[institutions.RobinhoodInstrument]:
        """Retrieve many instruments by supplied instrument_ids list"""
