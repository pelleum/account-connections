from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas import institutions


class IInstitutionRepo(ABC):
    @abstractmethod
    async def create(
        self, connection_data: institutions.CreateConnectionRepoAdapter
    ) -> None:
        """Create connection data"""

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
    ) -> None:
        """Update a signle user-institution connection by connection_id"""

    @abstractmethod
    async def retrieve_many_institution_connections(
        self,
        user_id: int = None,
        institution_id: int = None,
        page_number: int = 1,
        page_size: int = 200,
    ) -> List[institutions.InstitutionConnection]:
        """Retrieve many institution connections"""
