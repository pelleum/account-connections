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
    ROBINHOOD_INSTRUMENTS,
)
from app.infrastructure.db.models.portfolio import PORTFOLIOS
from app.libraries import pelleum_errors


class InstitutionRepo(IInstitutionRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, connection_data: institutions.CreateConnectionRepoAdapter
    ) -> institutions.InstitutionConnection:
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

        return await self.retrieve_institution_connection(
            user_id=connection_data.user_id,
            institution_id=connection_data.institution_id,
        )

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
    ) -> institutions.InstitutionConnection:
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

        return await self.retrieve_institution_connection(connection_id=connection_id)

    async def retrieve_many_institution_connections(
        self,
        user_id: int = None,
        institution_id: int = None,
        is_active: bool = None,
        page_number: int = 1,
        page_size: int = 10000,
    ) -> List[institutions.InstitutionConnection]:
        """Retrieve many institution connections"""

        conditions = []

        if user_id:
            conditions.append(INSTITUTION_CONNECTIONS.c.user_id == user_id)

        if institution_id:
            conditions.append(
                INSTITUTION_CONNECTIONS.c.institution_id == institution_id
            )

        if is_active:
            conditions.append(INSTITUTION_CONNECTIONS.c.is_active == is_active)

        j = INSTITUTION_CONNECTIONS.join(
            INSTITUTIONS,
            INSTITUTION_CONNECTIONS.c.institution_id == INSTITUTIONS.c.institution_id,
        ).join(PORTFOLIOS, INSTITUTION_CONNECTIONS.c.user_id == PORTFOLIOS.c.user_id)

        query = (
            select(
                [
                    INSTITUTION_CONNECTIONS,
                    INSTITUTIONS.c.name,
                    PORTFOLIOS.c.portfolio_id,
                ]
            )
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(INSTITUTION_CONNECTIONS.c.created_at))
        )

        query_results = await self.db.fetch_all(query)

        return [
            institutions.ConnectionJoinInstitutionJoinPortfolio(**result)
            for result in query_results
        ]

    async def create_robinhood_instrument(
        self, instrument_id: str, name: str, symbol: str
    ) -> None:
        """Creates Robinhood instrument in our DB for future reference"""

        create_instrument_statement = ROBINHOOD_INSTRUMENTS.insert().values(
            instrument_id=instrument_id, name=name, symbol=symbol
        )

        await self.db.execute(create_instrument_statement)

    async def retrieve_robinhood_instruments(
        self, instrument_ids: list
    ) -> List[institutions.RobinhoodInstrument]:
        """Retrieve many instruments by supplied instrument_ids list"""

        query = select(
            ROBINHOOD_INSTRUMENTS,
            ROBINHOOD_INSTRUMENTS.c.instrument_id.in_(instrument_ids),
        )

        query_results = await self.db.fetch_all(query)

        return [institutions.RobinhoodInstrument(**result) for result in query_results]
