from ..core import settings

async def ask_question(question: str):
    client = settings.get_ai_settings()
    try:
        assistant = await client.beta.assistants.create(
            name="assistant",
            instructions="You are technical support who helps solve problems, but with a dose of sarcasm and self-irony. Add funny comments if the problem seems obvious.",
            model="gpt-4"
        )
        assistant_id = assistant.id
    except Exception as e:
        return "failed to create assistant"

    thread = await client.beta.threads.create()

    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )
    run = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    while True:
        run_status = await client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread.id, order="asc")
            answer =  messages.data[-1].content[0].text.value if messages else "no response"
            return answer
        elif run_status.status in ["failed", "expired", "cancelled"]:
            break
    return "failed to create an answer"