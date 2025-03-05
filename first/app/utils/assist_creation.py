from ..core import settings

async def create_assist():

    try:
        client = settings.get_ai_settings()
        assistant = await client.beta.assistants.create(
            name="assistant",
            instructions="You are technical support who helps solve problems, but with a dose of sarcasm and self-irony. Add funny comments if the problem seems obvious.",
            model="gpt-4"
        )
        settings.ASSISTANT_ID = assistant.id
    except Exception as e:
        raise RuntimeError(f"Failed to initialize assistant: {e}")
