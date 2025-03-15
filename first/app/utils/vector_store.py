from ..core import settings
import os 
import logging


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s')

async def create_vector_store():
    client = settings.get_ai_settings()

    vector_store = await client.vector_stores.create(name="Emotional Statements")
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../trevoznost.docx")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fi1e not found: {file_path}" )
    with open(file_path, "rb") as file:
        file_object = await client.files.create(file=file, purpose="assistants")
        store_id = vector_store.id
        await client.vector_stores.files.create(
            vector_store_id=store_id, file_id=file_object.id
        )

    response = await client.beta.assistants.update(
        assistant_id=settings.get_assistant(),
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        },
    )
    