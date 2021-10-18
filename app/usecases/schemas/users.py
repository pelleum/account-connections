from datetime import datetime

from pydantic import BaseModel


class UserInDB(BaseModel):
    """Database Model"""

    user_id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
