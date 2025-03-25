from collections.abc import AsyncIterator
from typing import Callable
from agents import Agent, Runner, TResponseInputItem
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper


client_agent = Agent(
    name="customer", 
    instructions="Тебя зовут Василий Петрович, ты спокойны мужик из города Борисова. Ты звонишь в колл-центр магазина автозапчастей, чтобы заказать подшипники на свою audio 80, vin номер ты знаешь - вот он 9382929498239. Акцент у тебя грузинский, эмоциональность - спокойный, но иногда твоя интонация завышена, когда тебя плохо слышат и понимают. Скорость речи средняя.",
    model="gpt-4o-mini"
)
class MyWorkflow(VoiceWorkflowBase):
    def __init__ (self, on_start: Callable[[str], None]):
        self._input_history: list[TResponseInputItem] = []
        self._current_agent = client_agent
        self._on_start = on_start

    async def run(self, transcription: str) -> AsyncIterator:
        self._on_start(transcription)
        self._input_history.append({"role": "user", 
                                    "content": transcription})
        
        result = Runner.run_streamed(self._current_agent, self._input_history)

        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            yield chunk

        self._input_history = result.to_input_list()
        self._current_agent = result.last_agent