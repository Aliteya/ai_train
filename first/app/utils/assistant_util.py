from ..core import settings
from .thread_util import get_thread, send_amplitude_event
from ..repository import save_value
from ..logging import logger

from aiogram.fsm.context import FSMContext
import json


async def validate(value_text: str) -> bool:
    client = settings.get_ai_settings()
    prompt = (
            "User Loves or hate value?"
            "Answer strictly with 'yes' or 'no' without any additional text.\n\n"
            f"Value: {value_text}"
        )
    response = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0.0
    )
    logger.info(f"{response}")
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
        
        send_amplitude_event(
            user_id=str(user_id),
            event_type="value_saved",
            event_properties={
                "value": value_text
            }
        )
        await save_value(user_id=user_id, value=value_text)
        logger.info(f"Value '{value_text}' saved successfully")
        return f"Value '{value_text}' saved successfully"

    except Exception as e:
        logger.exception(f"Error processing tool {tool.id}: {e}")
        return f"Error processing tool {tool.id}: {e}"
    
async def ask_question(user_id: str, question: str, state: FSMContext):
    client = settings.get_ai_settings()
    assistant_id = settings.get_assistant()
    
    thread_id = await get_thread(state)

    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    if run.status == "requires_action":
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
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
                    logger.exception(f"Failed to submit tool outputs: {e}")
                    return f"Failed to submit tool outputs. Error: {e}"  
             
    if run.status == "completed":
        messages = await client.beta.threads.messages.list(thread_id=thread_id)
        assistant_messages = [
            msg for msg in messages.data if msg.role == "assistant"
        ]
        last_message = assistant_messages[0]
        answer = last_message.content[0].text.value.strip()
        return answer
    return f"Failed to create an answer. Run status {run.status}"