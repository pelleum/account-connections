from fastapi import HTTPException, status


login_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_user_error = HTTPException(status_code=400, detail="Inactive user")


class AccountAlreadyExists:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def account_exists(self):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.detail
            if self.detail
            else "An account with this username or email already exists.",
        )


class PasswordValidationError:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def invalid_password(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "The submitted password is invalid.",
        )


class EmailValidationError:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def invalid_email(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "The submitted email is invalid.",
        )


class InvalidResourceId:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def invalid_resource_id(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.detail
            if self.detail
            else "The supplied resource ID is invalid.",
        )


class UniqueConstraint:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def unique_constraint(self):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.detail
            if self.detail
            else "The supplied resource ID is invalid.",
        )


no_supplied_query_params = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="No supplied query parameters. Please supply query parameters.",
)

array_too_long = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The maximum amount of supporting sources is 10.",
)
