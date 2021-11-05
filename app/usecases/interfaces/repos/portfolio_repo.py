from abc import ABC, abstractmethod
from typing import List, Optional


from app.usecases.schemas import portfolios


class IPortfolioRepo(ABC):
    @abstractmethod
    async def create_portfolio(self, user_id: int, aggregated_value: float) -> None:
        """Creates new portfolio"""

    @abstractmethod
    async def retrieve_portfolio(
        self, user_id: str
    ) -> Optional[portfolios.PortfolioInDB]:
        """Retrieve portfolio by user_id"""

    @abstractmethod
    async def retrieve_all_portfolios(self) -> List[portfolios.PortfolioInDB]:
        """Retrieve all Pelleum portfolios"""

    @abstractmethod
    async def create_asset(self, new_asset: portfolios.CreateAssetRepoAdapter) -> None:
        """Creates new asset"""

    @abstractmethod
    async def update_asset(
        self,
        portfolio_id: int,
        asset_symbol: str,
        institution_id: int,
        updated_asset: portfolios.UpdateAssetRepoAdapter,
    ) -> None:
        """
        Update an individual asset holding by the composite index, (portfolio_id,
        asset_symbol, and institution_id)
        """

    @abstractmethod
    async def retrieve_asset(
        self,
        asset_id: int = None,
        portfolio_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""

    @abstractmethod
    async def retrieve_brokerage_assets(
        self,
        portfolio_id: int,
        institution_id: str,
    ) -> List[portfolios.AssetInDB]:
        """Retrieve all assets in a linked brokerage by portfolio_id"""

    @abstractmethod
    async def delete_asset(self, asset_id: int) -> None:
        """Delete asset"""
