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


class PelleumErrors:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def account_exists(self):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.detail
            if self.detail
            else "An account with this username or email already exists.",
        )

    async def invalid_password(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "The submitted password is invalid.",
        )

    async def invalid_email(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "The submitted email is invalid.",
        )

    async def invalid_resource_id(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.detail
            if self.detail
            else "The supplied resource ID is invalid.",
        )

    async def unique_constraint(self):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.detail if self.detail else "This resource already exists.",
        )

    async def client_error(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "There was an client error.",
        )

    async def general_error(self):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.detail
            if self.detail
            else "There was an internal server error.",
        )

    async def account_connection_error(self):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.detail
            if self.detail
            else "There was an external account connection error.",
        )


no_supplied_query_params = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="No supplied query parameters. Please supply query parameters.",
)

array_too_long = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The maximum amount of supporting sources is 10.",
)


class ExternalError:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def robinhood(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "The supplied mfa code is invalid.",
        )
