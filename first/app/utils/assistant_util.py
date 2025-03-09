from ..core import settings
from ..repository import save_value
import json
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s')

async def get_thread(user_id: str): 
    redis_client = settings.get_thread_db()
    thread_id = redis_client.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id 
    
async def validate(value_text: str) -> bool:
    client = settings.get_ai_settings()
    prompt = (
            "Is the following value meaningful and appropriate? User Loves or Dislikes value? "
            "Answer strictly with 'yes' or 'no' without any additional text.\n\n"
            f"Value: {value_text}"
        )
    response = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        # max_tokens=3,
        temperature=0.0
        # stop=["\n"]
    )
    logger.warning(f"{response}")
    answer = response.choices[0].text.strip().lower()
    return answer == "yes"
    

async def value_interceptor_processing(user_id: str, run, tool):
    try:
        arguments = json.loads(tool.function.arguments)
        value_text = arguments.get("value")

        if not value_text:
            logger.error(f"Value text is missing in tool arguments: {tool.function.arguments}")
            return "Error: Value text is missing"

        is_valid = await validate(value_text)
        if not is_valid:
            logger.warning(f"Validation failed for value: {value_text}")
            return f"Validation failed for value: {value_text}"
        
        await save_value(user_id=user_id, value=value_text)
        logger.info(f"Value '{value_text}' saved successfully")
        return f"Value '{value_text}' saved successfully"

    except Exception as e:
        logger.error(f"Error processing tool {tool.id}: {e}")
        return f"Error processing tool {tool.id}: {e}"
    
async def ask_question(user_id: str, question: str):
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
    logger.debug(f"Run status: {run.status}", run)

    if run.status == "completed":
        messages = await client.beta.threads.messages.list(thread_id=thread_id, order="asc")
        answer =  messages.data[-1].content[0].text.value if messages else "no response"
        logger.debug(answer)

    if run.status == "requires_action":
        logger.debug("requires_action")
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            logger.debug(tool, tool.function.name, tool.function.arguments)
            if tool.function.name == "save_value":
                    output = await value_interceptor_processing(user_id, run, tool)
                    tool_outputs.append({
                            "tool_call_id": tool.id,
                            "output": output
                        })
        if tool_outputs:
            try:
                    run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
            except Exception as e:
                    logger.error(f"Failed to submit tool outputs: {e}")
                    return f"Failed to submit tool outputs. Error: {e}"  
             
    if run.status == "completed":
        messages = await client.beta.threads.messages.list(thread_id=thread_id, order="asc")
        answer =  messages.data[-1].content[0].text.value if messages else "no response"
        return answer
    return f"Failed to create an answer. Run status {run.status}"