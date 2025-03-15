from ..database import connection
from ..models import Treasure
from ..logging import logger 

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

@connection
async def save_value(session: AsyncSession, user_id: int, value: str):
    try:
        new_treasure = Treasure(user_id=str(user_id), treasure_value=value)
        session.add(new_treasure)
        logger.info("create_new_treasure: Added new Treasure to the session")
        await session.flush()
        await session.commit()
        return new_treasure
    except IntegrityError as e:
        await session.rollback()
        logger.warning("duplicate value")
    except Exception as e:
        logger.exception(f"create_new_treasure:{str(e)}")
        await session.rollback()
