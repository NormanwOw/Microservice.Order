from typing import Any, Iterable, Type, cast

from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from src.application.ports.repositories import ISQLAlchemyRepository, T


class SQLAlchemyRepository(ISQLAlchemyRepository):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def add(self, data: T) -> T:
        self.session.add(data)
        await self.session.flush()
        return data

    async def find_all(
        self,
        filter_field: InstrumentedAttribute[Any] | None = None,
        filter_value: Any = None,
        order_by: InstrumentedAttribute[Any] | None = None,
    ) -> list[T]:
        if not filter_field or not filter_value:
            if order_by:
                res = await self.session.execute(select(self.model).order_by(desc(order_by)))
            else:
                res = await self.session.execute(select(self.model))
            return list(cast(Iterable[T], res.scalars().all()))

        if order_by:
            query = select(self.model).where(filter_field == filter_value).order_by(desc(order_by))
        else:
            query = select(self.model).where(filter_field == filter_value)
        res = await self.session.execute(query)
        return list(cast(Iterable[T], res.scalars().all()))

    async def find_one(  # type: ignore
        self, filter_field: InstrumentedAttribute[Any] | None = None, filter_value: Any = None
    ) -> T | None:
        if filter_field and filter_value:
            query = select(self.model).where(filter_field == filter_value)
        else:
            query = select(self.model)
        res = await self.session.execute(query)
        return cast(T | None, res.scalars().first())

    async def update(
        self,
        values: dict[str, Any],
        filter_field: InstrumentedAttribute[Any] | None = None,
        filter_value: Any = None,
    ) -> None:
        if filter_field and filter_value:
            stmt = update(self.model).values(**values).where(filter_field == filter_value)
        else:
            stmt = update(self.model).values(**values)
        await self.session.execute(stmt)

    async def delete_one(self, filter_field: InstrumentedAttribute[Any], filter_value: Any) -> None:
        await self.session.execute(delete(self.model).where(filter_field == filter_value))

    async def delete(self) -> None:
        await self.session.execute(delete(self.model))
