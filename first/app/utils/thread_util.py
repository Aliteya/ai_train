from ..core import settings
from amplitude import BaseEvent
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

thread_pool_executor = ThreadPoolExecutor(max_workers=5)

def run_in_thread_pool(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return thread_pool_executor.submit(func, *args, **kwargs)
    return wrapper

@run_in_thread_pool
def send_amplitude_event(user_id: str, event_type: str, event_properties: dict = None):
    try:
        amplitude_client = settings.get_amplitude_token()
        event = BaseEvent(
            user_id=user_id,
            event_type=event_type,
            event_properties=event_properties or {}
        )
        amplitude_client.track(event)
    except Exception as e:
        print(f"Failed to send event to Amplitude: {e}")

async def get_thread(user_id: str): 
    redis_client = settings.get_thread_db()
    thread_id = redis_client.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id 