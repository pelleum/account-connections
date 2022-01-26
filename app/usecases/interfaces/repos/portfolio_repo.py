from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas import portfolios


class IPortfolioRepo(ABC):
    @abstractmethod
    async def upsert_asset(self, new_asset: portfolios.UpsertAssetRepoAdapter) -> None:
        """Creates new asset"""

    @abstractmethod
    async def update_asset(
        self,
        user_id: int,
        asset_symbol: str,
        institution_id: int,
        updated_asset: portfolios.UpdateAssetRepoAdapter,
    ) -> None:
        """
        Update an individual asset holding by the composite index, (user_id,
        asset_symbol, and institution_id)
        """

    @abstractmethod
    async def retrieve_asset(
        self,
        asset_id: int = None,
        user_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""

    @abstractmethod
    async def retrieve_brokerage_assets(
        self,
        user_id: int,
        institution_id: str,
    ) -> List[portfolios.AssetInDB]:
        """Retrieve all assets in a linked brokerage by user_id"""

    @abstractmethod
    async def delete_asset(self, asset_id: int) -> None:
        """Delete asset"""
