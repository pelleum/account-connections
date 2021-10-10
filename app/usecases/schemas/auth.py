from typing import Optional

from pydantic import BaseModel


class JWTData(BaseModel):
    username: Optional[str] = None
