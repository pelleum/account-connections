from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.dependencies import get_users_repo  # pylint: disable = cyclic-import
from app.libraries import pelleum_errors
from app.settings import settings
from app.usecases.interfaces.repos.user_repo import IUsersRepo
from app.usecases.schemas import auth
from app.usecases.schemas.users import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.token_url)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates token sent in"""
    try:
        payload = jwt.decode(
            token,
            settings.json_web_token_secret,
            algorithms=[settings.json_web_token_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise pelleum_errors.invalid_credentials
        token_data = auth.JWTData(username=username)
    except JWTError:
        raise pelleum_errors.invalid_credentials  # pylint: disable = raise-missing-from

    return await verify_user_exists(username=token_data.username)


async def verify_user_exists(username: str):
    users_repo = await get_users_repo()
    user: UserInDB = await users_repo.retrieve_user_with_filter(username=username)
    if user is None:
        raise pelleum_errors.invalid_credentials
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise pelleum_errors.inactive_user_error
    return current_user
