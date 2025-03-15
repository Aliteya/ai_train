from ..core import settings
from ..logging import logger

import os 

async def create_vector_store():
    client = settings.get_ai_settings()
    vector_store = await client.vector_stores.create(name="Emotional Statements")
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../anxiety.docx")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}" )
    
    with open(file_path, "rb") as file:
        logger.info("create vector store")
        file_object = await client.files.create(file=file, purpose="assistants")
        store_id = vector_store.id
        await client.vector_stores.files.create(
            vector_store_id=store_id, file_id=file_object.id
        )

    response = await client.beta.assistants.update(
        assistant_id=settings.get_assistant(),
        # instructions="Do not mention file names or sources in your answers. Give answers directly, without citing any documents other than the one at the very end.",
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        },
    )
    