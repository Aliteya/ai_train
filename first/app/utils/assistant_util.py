from ..core import settings

async def get_thread(user_id): 
    redis_client = settings.get_db()
    thread_id = redis_client.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id 


async def ask_question(user_id, question: str):
    client = settings.get_ai_settings()
    redis_client = settings.get_thread_db()
    assistant_id = settings.get_assistant()
    
    thread_id = await get_thread(user_id)
    if not thread_id: 
        thread = await client.beta.threads.create()
        redis_client.set(f"user:{user_id}:thread_id", thread.id)
        thread_id = thread.id
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    
    if run.status == "completed":
        messages = await client.beta.threads.messages.list(thread_id=thread_id, order="asc")
        answer =  messages.data[-1].content[0].text.value if messages else "no response"
        return answer

    return "Failed to create an answer"