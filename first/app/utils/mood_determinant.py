from ..core import settings
from .thread_util import get_thread
from .file_util import upload_photo
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s')

async def mood_determination(user_id, image_file):
    try:
        client = settings.get_ai_settings()
        redis_client = settings.get_thread_db()
        assistant_id = settings.get_assistant()
        logger.info(f"Initialized AI settings for user {user_id}")

        thread_id = await get_thread(user_id)
        if not thread_id:
            thread = await client.beta.threads.create()
            redis_client.set(f"user:{user_id}:thread_id", thread.id)
            thread_id = thread.id
            logger.info(f"Created new thread for user {user_id}: {thread_id}")
        else:
            logger.info(f"Using existing thread for user {user_id}: {thread_id}")

        file_id = await upload_photo(image_file, user_id)
        logger.info(f"Uploaded photo with file ID: {file_id}")

        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=[
                {
                    "type": "text",
                    "text": "Determine the mood from the photo. Answer as briefly as possible, preferably in one or more words."
                },
                {
                    "type": "image_file",
                    "image_file": {
                        "file_id": file_id
                    }
                }
            ]
        )
        logger.info("Message with photo added to the thread.")

        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        logger.info(f"Run completed with status: {run.status}")

        if run.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread_id)
            logger.warning(f"Messages retrieved from thread: {messages}")

            assistant_messages = [
                msg for msg in messages.data if msg.role == "assistant"
            ]
            if not assistant_messages:
                logger.error("No assistant messages found in the thread.")
                raise Exception("No assistant response found.")

            last_message = assistant_messages[0]
            answer = last_message.content[0].text.value.strip()
            logger.info(f"Mood determined: {answer}")
            return answer
        else:
            logger.error(f"Run failed with status: {run.status}")
            raise Exception(f"Run failed with status: {run.status}")

    except Exception as e:
        logger.exception(f"Error in mood_determination for user {user_id}: {e}")
        raise
# async def mood_determination(user_id, image_file):
#     client = settings.get_ai_settings()
#     redis_client = settings.get_thread_db()
#     assistant_id = settings.get_assistant()
    
#     thread_id = await get_thread(user_id)
#     if not thread_id: 
#         thread = await client.beta.threads.create()
#         redis_client.set(f"user:{user_id}:thread_id", thread.id)
#         thread_id = thread.id

#     await client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=[
#             {
#                 "type": "text",
#                 "text" : "Determine the mood from the photo. Answer as briefly as possible, preferably in one or more words."
#             },
#             {
#                 "type": "image_file",
#                 "image_file": {
#                     "file_id": await upload_photo(image_file, user_id)
#                 }
#             }
#         ]
#     )

#     run = await client.beta.threads.runs.create_and_poll(
#         thread_id=thread_id,
#         assistant_id=assistant_id
#     )

#     if run.status == "completed":
#         messages = await client.beta.threads.messages.list(thread_id=thread_id)
#         logging.warning(messages)
#         assistant_messages = [
#             msg for msg in messages.data if msg.role == "assistant"
#         ]
#         last_message = assistant_messages[0]
#         answer = last_message.content[0].text.value.strip()
#         return answer
#     else:
#         raise Exception(f"Run failed with status: {run.status}")