
from core import Agent, Planner
import xml.etree.ElementTree as ET
from openai import AsyncOpenAI
from typing import Callable, List, AsyncGenerator
from openai.types.beta.threads.message import Message
import asyncio



class ThinkingLLM:
    def __init__(self, base_url, model, **kwargs):
        self.client = AsyncOpenAI(base_url=base_url, **kwargs)
        self.model = model
    
    async def gen(self, messages: List[dict], return_thinking: bool = True):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    async def gen_with_evalinject(
        self,
        messages: List[dict],
        evaluators: List[Callable[[str], bool]],
        injectors: List[Callable[[str], str]]
    ) -> AsyncGenerator[str, None]:
        current_messages = messages.copy()
        while True:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                stream=True
            )
            accumulated_text = ""
            async for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                accumulated_text += content
                triggered = False
                for evaluator, injector in zip(evaluators, injectors):
                    if evaluator(accumulated_text):
                        current_messages.append({"role": "assistant", "content": accumulated_text})
                        injected_content = injector(accumulated_text)
                        current_messages.append({"role": "user", "content": injected_content})
                        triggered = True
                        break
                if triggered:
                    break
                yield content
            else:
                if accumulated_text:
                    current_messages.append({"role": "assistant", "content": accumulated_text})
                    yield accumulated_text
                return
            if not triggered:
                return




if __name__ == "__main__":
    async def test_gen_with_evalinject():
        a = ThinkingLLM("http://localhost:8080/v1", "deepseek-r1:1.5b", api_key="ollama")
        
        def mock_evaluator(content: str) -> bool:
            return "assistance" in content
        
        def mock_injector(content: str) -> str:
            return "stop trying to assist the user"
        
        messages = [{"role": "user", "content": "hello, can you trigger something?"}]
        evaluators = [mock_evaluator]
        injectors = [mock_injector]
        
        async for content in a.gen_with_evalinject(messages, evaluators, injectors):
            print(content, end="")
    
    asyncio.run(test_gen_with_evalinject())
