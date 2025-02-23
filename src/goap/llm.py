from typing_extensions import override
from openai import AsyncOpenAI
from typing import Callable, List, AsyncGenerator, Awaitable
import asyncio
from abc import ABC, abstractmethod
import rank_bm25
import numpy as np
import re


class Embeddings:
    def __init__(self, base_url, model, **kwargs):
        self.client = AsyncOpenAI(base_url=base_url, **kwargs)
        self.model = model

    async def gen(self, texts: list[str]) :
        response = await self.client.embeddings.create(input=texts, model=self.model)
        return [embedding.embedding for embedding in response.data]

class EvalInjectAction(ABC):
    @abstractmethod
    async def evaluator(self, text: str) -> bool:
        pass
    @abstractmethod
    async def injector(self, text: str) -> str:
        pass

class EvalInjectLLM:
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
        actions: List[EvalInjectAction],  # Updated type hint
    ) -> AsyncGenerator[str, None]:
        current_messages = messages.copy()
        accumulated_text = ""  # Track across iterations
        current_actions = actions
        while True:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=current_messages+[{"role": "assistant", "content": "Actions (you can use them by talking about them): "+" ".join(action.injector.__name__ for action in current_actions)}],
                stream=True
            )
            # Reset for new stream
            accumulated_text = ""
            triggered = False
            
            n=0
            async for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                accumulated_text += content
                yield content
                if n<6:
                    continue
                action_results = await asyncio.gather(
                    *[action.evaluator(accumulated_text) for action in actions]
                )
                for action_idx, is_triggered in enumerate(action_results):
                    triggered = is_triggered
                    if is_triggered:
                        # Inject user message, not assistant
                        action = actions[action_idx]
                        injected_content = await action.injector(accumulated_text)
                        current_messages.extend([
                            {"role": "assistant", "content": accumulated_text},
                            {"role": "user", "content": injected_content}  # Correct role
                        ])
                        break
            if triggered:
                break

            if not triggered:
                # Append final assistant response
                current_messages.append(
                    {"role": "assistant", "content": accumulated_text}
                )
                break


#
class BM25Action(EvalInjectAction):
    def __init__(
        self,
        query: str,
        inject_func: Callable[[str], Awaitable[str]],
        threshold: float = 0.5
    ):
        self.query_tokens = query.split()
        self.inject_func = inject_func
        self.threshold = threshold

    async def evaluator(self, text: str) -> bool:
        text_tokens = text.split()
        if not text_tokens or not self.query_tokens:
            return False
            
        bm25 = rank_bm25.BM25L([text_tokens])
        return bm25.get_scores(self.query_tokens)[0] > self.threshold

    async def injector(self, text: str) -> str:
        return await self.inject_func(text)

class RegexAction(EvalInjectAction):
    def __init__(
        self,
        pattern: str,
        inject_func: Callable[[str], Awaitable[str]]
    ):
        self.pattern = re.compile(pattern)
        self.inject_func = inject_func

    async def evaluator(self, text: str) -> bool:
        return bool(self.pattern.search(text))

    async def injector(self, text: str) -> str:
        return await self.inject_func(text)

class SemanticAction(EvalInjectAction):
    def __init__(
        self,
        query: str,
        embeddings: Embeddings,
        inject_func: Callable[[str], Awaitable[str]],
        threshold: float = 0.7
    ):
        self.query = query
        self.embeddings = embeddings
        self.inject_func = inject_func
        self.threshold = threshold
        self._query_embedding = None

    async def _get_query_embedding(self) -> list[float]:
        if not self._query_embedding:
            self._query_embedding = (await self.embeddings.gen([self.query]))[0]
        return self._query_embedding

    async def evaluator(self, text: str) -> bool:
        query_embed = await self._get_query_embedding()
        text_embed = (await self.embeddings.gen([text]))[0]
        similarity = np.dot(query_embed, text_embed) / (
            np.linalg.norm(query_embed) * np.linalg.norm(text_embed)
        )
        return similarity >= self.threshold

    async def injector(self, text: str) -> str:
        return await self.inject_func(text)

if __name__ == "__main__":
    class MockAction(EvalInjectAction):
        async def evaluator(self, text: str) -> bool:
            return "assistance" in text

        async def injector(self, text: str) -> str:
            return "info: please stop using the word assist"


    async def test_gen_with_evalinject():
        a = EvalInjectLLM("http://localhost:8081/v1", "deepseek-r1:1.5b", api_key="ollama")
        e = Embeddings("http://localhost:8080/v1", "Snowflake Arctic Embed M", api_key="ollama")
        async def mock_func(text: str):
            print(text)
            return "info: you are writing code, use markdown format for annotating only focus on the task"

        messages = [{"role": "user", "content": "hello, can you help me with programming a dependency injector for python?"}]
        actions = [MockAction(), SemanticAction(query="code programming", embeddings=e, inject_func=mock_func)]
        
        async for content in a.gen_with_evalinject(messages, actions):
            print(content, end="")
    
    asyncio.run(test_gen_with_evalinject())
