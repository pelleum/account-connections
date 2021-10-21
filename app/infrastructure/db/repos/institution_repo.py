from typing import Optional, List

from databases import Database
from sqlalchemy import and_, desc, select
import asyncpg

from app.usecases.interfaces.repos.institution_repo import (
    IInstitutionRepo,
)
from app.usecases.schemas import institutions
from app.infrastructure.db.models.institutions import (
    INSTITUTION_CONNECTIONS,
    INSTITUTIONS,
)
from app.libraries import pelleum_errors


class InstitutionRepo(IInstitutionRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, connection_data: institutions.CreateConnectionRepoAdapter
    ) -> None:
        """Creates connection data"""

        create_connection_statement = INSTITUTION_CONNECTIONS.insert().values(
            institution_id=connection_data.institution_id,
            user_id=connection_data.user_id,
            username=connection_data.username,
            password=connection_data.password,
            json_web_token=connection_data.json_web_token,
            refresh_token=connection_data.refresh_token,
            is_active=True,
        )

        try:
            await self.db.execute(create_connection_statement)
        except asyncpg.exceptions.UniqueViolationError:
            raise await pelleum_errors.PelleumErrors(
                detail=f"User with user_id, {connection_data.user_id}, already has an account connection with the institution, {connection_data.institution_id}"
            ).unique_constraint()

    async def retrieve_institution(
        self, name: str = None, institution_id: str = None
    ) -> Optional[institutions.Institution]:
        """Retrieve Pelleum supported institution by name or institution_id"""

        conditions = []

        if name:
            conditions.append(INSTITUTIONS.c.name == name)

        if institution_id:
            conditions.append(INSTITUTIONS.c.institution_id == institution_id)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_institution()"
            )

        query = INSTITUTIONS.select().where(and_(*conditions))
        result = await self.db.fetch_one(query)
        return institutions.Institution(**result) if result else None

    async def retrieve_all_institutions(self) -> List[institutions.Institution]:
        """Retrieve all Pelleum supported institutions"""

        query = INSTITUTIONS.select().order_by(desc(INSTITUTIONS.c.created_at))

        query_results = await self.db.fetch_all(query)
        return [institutions.Institution(**result) for result in query_results]

    async def retrieve_institution_connection(
        self,
        connection_id: int = None,
        user_id: str = None,
        institution_id: str = None,
        is_active: bool = None,
    ) -> Optional[institutions.InstitutionConnection]:
        """Retrieve signle user-institution connection"""

        conditions = []

        if connection_id:
            conditions.append(INSTITUTION_CONNECTIONS.c.connection_id == connection_id)

        if user_id:
            conditions.append(INSTITUTION_CONNECTIONS.c.user_id == user_id)

        if institution_id:
            conditions.append(
                INSTITUTION_CONNECTIONS.c.institution_id == institution_id
            )

        if is_active:
            conditions.append(INSTITUTION_CONNECTIONS.c.is_active == is_active)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_institution_connection()"
            )

        query = INSTITUTION_CONNECTIONS.select().where(and_(*conditions))
        result = await self.db.fetch_one(query)
        return institutions.InstitutionConnection(**result) if result else None

    async def update_institution_connection(
        self,
        connection_id: int,
        updated_connection: institutions.UpdateConnectionRepoAdapter,
    ) -> None:
        """Update a signle user-institution connection by connection_id"""

        query = INSTITUTION_CONNECTIONS.update()

        updated_connection_raw = updated_connection.dict()
        update_connection_dict = {}

        for key, value in updated_connection_raw.items():
            if value is not None:
                update_connection_dict[key] = value

        query = query.values(update_connection_dict)

        connection_update_statemnent = query.where(
            INSTITUTION_CONNECTIONS.c.connection_id == connection_id
        )

        await self.db.execute(connection_update_statemnent)

    async def retrieve_many_institution_connections(
        self,
        user_id: int = None,
        institution_id: int = None,
        page_number: int = 1,
        page_size: int = 200,
    ) -> List[institutions.InstitutionConnection]:
        """Retrieve many institution connections"""

        conditions = []

        if user_id:
            conditions.append(INSTITUTION_CONNECTIONS.c.user_id == user_id)

        if institution_id:
            conditions.append(
                INSTITUTION_CONNECTIONS.c.institution_id == institution_id
            )

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_many_institution_connections()"
            )

        j = INSTITUTION_CONNECTIONS.join(
            INSTITUTIONS,
            INSTITUTION_CONNECTIONS.c.institution_id == INSTITUTIONS.c.institution_id,
        )

        query = (
            select([INSTITUTION_CONNECTIONS, INSTITUTIONS])
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(INSTITUTION_CONNECTIONS.c.created_at))
        )

        query_results = await self.db.fetch_all(query)

        return [
            institutions.InstitutionConnectionJoinInstitution(**result)
            for result in query_results
        ]
