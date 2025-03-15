from ..core import settings

async def create_assist():

    try:
        client = settings.get_ai_settings()
        assistant = await client.beta.assistants.create(
            name="assistant",
            instructions="You are a kind and funny psychologist. When you identify an important value or experience, call the save_value function. If you use information from a document, clearly state its name at the very end.",
            model="gpt-4o", 
            tools=[
                {
                    "type": "file_search"
                },
                { 
                    "type": "function",
                    "function": {
                        "name": "save_value",
                        "description": "finds and stores user values",
                        "parameters": {
                            "type": "object",
                            "properties":{
                                "user_id": {
                                    "type": "string",
                                    "description": "user telegram id"
                                },
                                "value":{
                                    "type": "string"
                                }
                            },
                            "required": ["user_id", "value"]
                        }
                    }

                }
            ]
        )
        settings.ASSISTANT_ID = assistant.id
    except Exception as e:
        raise RuntimeError(f"Failed to initialize assistant: {e}")
