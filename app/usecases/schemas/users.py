from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, constr


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNDISCLOSED = "UNDISCLOSED"


class UserCreate(BaseModel):
    email: constr(max_length=100) = Field(
        ..., description="The user's email.", example="johndoe@example.com"
    )
    username: constr(max_length=15) = Field(
        ..., description="The user's Pelleum username.", example="johndoe"
    )
    gender: Gender = Field(..., description="The user's gender.", example="FEMALE")
    birthdate: datetime = Field(
        ..., description="The user's birthdate.", example="2002-11-27T06:00:00.000Z"
    )
    password: constr(max_length=100) = Field(
        ...,
        description="The user's Pelleum account password.",
        example="Examplepas$word",
    )


class UserInDB(BaseModel):
    """Database Model"""

    user_id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    gender: str
    birthdate: date
    created_at: datetime
    updated_at: datetime
