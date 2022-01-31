from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas import institutions


class IInstitutionRepo(ABC):
    @abstractmethod
    async def upsert(
        self, connection_data: institutions.CreateConnectionRepoAdapter
    ) -> institutions.InstitutionConnection:
        """Creates connection data"""

    @abstractmethod
    async def retrieve_institution(
        self, name: str = None, institution_id: str = None
    ) -> Optional[institutions.Institution]:
        """Retrieve Pelleum supported institution by name or institution_id"""

    @abstractmethod
    async def retrieve_all_institutions(self) -> List[institutions.Institution]:
        """Retrieve all Pelleum supported institutions"""

    @abstractmethod
    async def retrieve_institution_connection(
        self,
        connection_id: int = None,
        user_id: str = None,
        institution_id: str = None,
        is_active: bool = None,
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
    async def retrieve_many_institution_connections(
        self,
        query_params: institutions.RetrieveManyConnectionsRepoAdapter,
        skip_locked: int = False,
        page_number: int = 1,
        page_size: int = 10000,
    ) -> List[institutions.ConnectionJoinInstitutionJoinPortfolio]:
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

    @abstractmethod
    async def delete(self, institution_id: int) -> None:
        """Delete connection"""
