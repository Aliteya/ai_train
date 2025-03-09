from ..database import connection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Treasure
import logging 


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s')


import logging

logger = logging.getLogger(__name__)

@connection
async def save_value(session, user_id, value):
    try:
        new_treasure = Treasure(user_id=str(user_id), treasure_value=value)
        session.add(new_treasure)
        logger.info("create_new_treasure: Added new Treasure to the session")
        await session.flush()
        await session.commit()
        return new_treasure

    except Exception as e:
        logger.error(f"create_new_treasure: Error occurred - {str(e)}", exc_info=True)
        await session.rollback()
        raise  
