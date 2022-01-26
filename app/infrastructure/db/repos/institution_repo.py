from typing import List, Optional

from databases import Database
from sqlalchemy import and_, desc, select
from sqlalchemy.dialects.postgresql import insert

from app.infrastructure.db.models.institutions import (
    INSTITUTION_CONNECTIONS,
    INSTITUTIONS,
    ROBINHOOD_INSTRUMENTS,
)
from app.usecases.interfaces.repos.institution_repo import IInstitutionRepo
from app.usecases.schemas import institutions


class InstitutionRepo(IInstitutionRepo):
    def __init__(self, db: Database):
        self.db = db

    async def upsert(
        self, connection_data: institutions.CreateConnectionRepoAdapter
    ) -> institutions.InstitutionConnection:
        """Creates connection data"""

        create_connection_statement = insert(INSTITUTION_CONNECTIONS).values(
            institution_id=connection_data.institution_id,
            user_id=connection_data.user_id,
            username=connection_data.username,
            password=connection_data.password,
            json_web_token=connection_data.json_web_token,
            refresh_token=connection_data.refresh_token,
            is_active=connection_data.is_active,
        )

        upsert_stmt = create_connection_statement.on_conflict_do_update(
            index_elements=[INSTITUTION_CONNECTIONS.c.user_id, INSTITUTION_CONNECTIONS.c.institution_id],
            set_=dict(
                username=connection_data.username,
                password=connection_data.password,
                json_web_token=connection_data.json_web_token,
                refresh_token=connection_data.refresh_token,
                is_active=connection_data.is_active
            )
        )

        new_connection_id = await self.db.execute(upsert_stmt)

        return await self.retrieve_institution_connection(
            connection_id=new_connection_id
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
        query_params: institutions.RetrieveManyConnectionsRepoAdapter,
        skip_locked: int = False,
        page_number: int = 1,
        page_size: int = 10000,
    ) -> List[institutions.ConnectionJoinInstitutionJoinPortfolio]:
        """Retrieve many institution connections"""

        conditions = []

        if query_params.user_id:
            conditions.append(INSTITUTION_CONNECTIONS.c.user_id == query_params.user_id)

        if query_params.institution_id:
            conditions.append(
                INSTITUTION_CONNECTIONS.c.institution_id == query_params.institution_id
            )

        if query_params.is_active:
            conditions.append(
                INSTITUTION_CONNECTIONS.c.is_active == query_params.is_active
            )

        if query_params.has_refresh_token:
            conditions.append(INSTITUTION_CONNECTIONS.c.refresh_token != None)

        if len(conditions) == 0:
            raise Exception(
                "Please supply query parameters to retrieve_many_institution_connections()"
            )

        j = INSTITUTION_CONNECTIONS.join(
            INSTITUTIONS,
            INSTITUTION_CONNECTIONS.c.institution_id == INSTITUTIONS.c.institution_id,
        )

        query = (
            select(
                [
                    INSTITUTION_CONNECTIONS,
                    INSTITUTIONS.c.name,
                ]
            )
            .select_from(j)
            .where(and_(*conditions))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
            .order_by(desc(INSTITUTION_CONNECTIONS.c.created_at))
        )

        if skip_locked:
            query = query.with_for_update(skip_locked=True)

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
            [ROBINHOOD_INSTRUMENTS],
            ROBINHOOD_INSTRUMENTS.c.instrument_id.in_(instrument_ids),
        )

        query_results = await self.db.fetch_all(query)

        return [institutions.RobinhoodInstrument(**result) for result in query_results]
