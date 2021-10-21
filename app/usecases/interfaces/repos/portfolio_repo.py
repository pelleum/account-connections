from abc import ABC, abstractmethod
from typing import List


from app.usecases.schemas import portfolios


class IPortfolioRepo(ABC):
    @abstractmethod
    async def create_portfolio(self, user_id: int, aggregated_value: float) -> None:
        """Creates new portfolio"""

    @abstractmethod
    async def create_asset(self, new_asset: portfolios.AssetRepoAdapter) -> None:
        """Creates new asset"""

    @abstractmethod
    async def retrieve_all_portfolios(self) -> List[portfolios.PortfolioInDB]:
        """Retrieve all Pelleum portfolios"""
