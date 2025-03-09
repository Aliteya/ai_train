from .core import treasure_db_settings
from .models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(treasure_db_settings.get_treasure_url(), echo=True, isolation_level="READ COMMITTED")

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
    return wrapper

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db_connections():
    try:
        await engine.dispose()
    except Exception as e:
        print(f"Ошибка при закрытии соединений: {e}")