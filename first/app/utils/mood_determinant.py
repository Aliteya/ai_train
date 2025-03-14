from ..core import settings
from .thread_util import get_thread
from .file_util import upload_photo
from ..logging import logger

from aiogram.fsm.context import FSMContext

async def mood_determination(user_id, image_file, state: FSMContext):
    try:
        client = settings.get_ai_settings()
        assistant_id = settings.get_assistant()
        logger.info(f"Initialized AI settings for user {user_id}")

        thread_id = await get_thread(state)

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
            assistant_messages = [
                msg for msg in messages.data if msg.role == "assistant"
            ]
            if not assistant_messages:
                logger.error("No assistant messages found in the thread.")
                raise Exception("No assistant response found.")

            last_message = assistant_messages[0]
            answer = last_message.content[0].text.value.strip()
            return answer
        else:
            logger.error(f"Run failed with status: {run.status}")
            raise Exception(f"Run failed with status: {run.status}")

    except Exception as e:
        logger.exception(f"Error in mood_determination for user {user_id}: {e}")
        raise