from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    thesis_id: Optional[int] = Field(
        None, description="The thesis ID that this asset is linked to.", example="29"
    )
    skin_rating: Optional[float] = Field(
        None,
        description="The skin in the game rating we assign to the individual asset holding.",
        example=9.8,
    )
    average_buy_price: Optional[float] = Field(
        None,
        description="The Pelleum user's average (per share) buy price.",
        example=657.23,
    )
    total_contribution: Optional[float] = Field(
        None,
        description="The total amount of US dollars the Pelleum user has contributed toward this specific asset holding.",
        example=39756.65,
    )


class UpdateAssetRepoAdapter(AssetBase):
    position_value: Optional[float] = Field(
        None,
        description="The total value of the asset positoin in US dollars.",
        example=102254.98,
    )


class AssetRepoAdapter(AssetBase):
    """Object sent to PortfolioRepo's create_asset()"""

    portfolio_id: int = Field(
        ...,
        description="The unique identifier of the Pelleum user's portfolio that this asset belongs to.",
        example="29",
    )
    asset_symbol: str = Field(
        ..., description="The asset's ticker symbol.", example="TSLA"
    )
    position_value: float = Field(
        ...,
        description="The total value of the asset positoin in US dollars.",
        example=102254.98,
    )


class AssetInDB(AssetRepoAdapter):
    """Database Model"""

    asset_id: int = Field(
        ...,
        description="The unique identifier of a Pelleum user's individually owned asset",
        example=1,
    )
    created_at: datetime = Field(
        ...,
        description="The time and date that the asset was created in our database.",
        example="2021-10-19 04:56:14.02395",
    )
    updated_at: datetime = Field(
        ...,
        description="The time and date that the asset was updated in our database.",
        example="2021-10-19 04:56:14.02395",
    )


class PortfolioInDB(BaseModel):
    """Database Model"""

    portfolio_id: int = Field(
        ...,
        description="The unique identifier of a user's Pelleum portfolio.",
        example=3473873,
    )
    user_id: int = Field(
        ...,
        description="The user ID associated with this Pelleum portfolio.",
        example=3454,
    )
    aggregated_value: float = Field(
        ...,
        description="The total value of the user's Pelleum portfolio in US dollars.",
        example=785943,
    )
    created_at: datetime = Field(
        ...,
        description="The time and date that the asset was created in our database.",
        example="2021-10-19 04:56:14.02395",
    )
    updated_at: datetime = Field(
        ...,
        description="The time and date that the asset was updated in our database.",
        example="2021-10-19 04:56:14.02395",
    )
