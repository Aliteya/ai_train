from ..core import settings

async def get_thread(user_id: str): 
    redis_client = settings.get_thread_db()
    thread_id = redis_client.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id 