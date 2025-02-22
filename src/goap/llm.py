from typing import Callable
from .core import Agent, Planner
import xml.etree.ElementTree as ET
from openai import AsyncOpenAI, AsyncAssistantEventHandler, AsyncStream


class EvalInjector(AsyncAssistantEventHandler):
    def __init__(self, evaluators: list[Callable], injectors: list[Callable]):
        super().__init__()
        self.evaluator = evaluators
        self.injector = injectors
        self.messages = []

    async def on_text_created(self, text) -> None:
        

    async def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    async def on_message_done(self, message: Message) -> None:
        pass
        

class ThinkingLLM:
    def __init__(self, base_url, **kwargs):
        self.generator = AsyncOpenAI(base_url=base_url, **kwargs).chat.completions.create
    
    async def gen(self, messages: list[dict[str, str]], return_thinking=True):
        if not messages:
            return
        text: str = await self.generator(messages=messages, model="")[0].message.content
        thinking = ET.fromstring(text).findall("think")
        thinking, response = thinking[0].text, thinking[0].tail
        return response, thinking

    def gen_with_evalinject(self, messages:list[dict[str, str]], evaluator: Callable, injector: Callable):
        pass      



class CoTPlanner(Planner):
    def __init__(self, name):
        self.name = name

    


