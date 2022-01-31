from datetime import datetime
from typing import Optional

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
    quantity: Optional[float] = Field(
        None,
        description="The total number of shares owned.",
        example=102254.98,
    )
    is_up_to_date: Optional[bool] = Field(
        None,
        description="Whether or not the asset resource is up to date with the linked brokerage.",
        example=True,
    )
    update_errors: Optional[str] = Field(
        None,
        description="An error during the periodic asset update process.",
        example="There was an error.",
    )


class UpsertAssetRepoAdapter(AssetBase):
    """Object sent to PortfolioRepo's upsert_asset()"""

    user_id: int = Field(
        ...,
        description="The unique identifier of the Pelleum user's portfolio that this asset belongs to.",
        example="29",
    )
    institution_id: str = Field(
        ...,
        description="The unique identifier of the Pelleum supported institution.",
        example="c29cdd1a-feca-40b6-a4e1-f49c3a21f2af",
    )
    name: Optional[str] = Field(None, description="The asset's name.", example="Tesla")
    asset_symbol: str = Field(
        ..., description="The asset's ticker symbol.", example="TSLA"
    )
    position_value: Optional[float] = Field(
        None,
        description="The total value of the asset positoin in US dollars.",
        example=102254.98,
    )
    quantity: float = Field(
        ...,
        description="The total number of shares owned.",
        example=102254.98,
    )


class AssetInDB(UpsertAssetRepoAdapter):
    """Database Model"""

    asset_id: int = Field(
        ...,
        description="The unique identifier of a Pelleum user's individually owned asset",
        example=1,
    )
    is_up_to_date: Optional[bool] = Field(
        None,
        description="Whether or not the asset resource is up to date with the linked brokerage.",
        example=True,
    )
    update_errors: Optional[str] = Field(
        None,
        description="An error during the periodic asset update process.",
        example="There was an error.",
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


class UsersInstitutionRepoAdapter(BaseModel):
    """Delete RepoAdapter"""

    user_id: int
    institution_id: str
