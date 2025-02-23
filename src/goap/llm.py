from typing_extensions import override
from openai import AsyncOpenAI
from typing import Callable, List, AsyncGenerator, Awaitable
import asyncio
from abc import ABC, abstractmethod
import rank_bm25
import numpy as np

class Resolver:
    def __init__(self) -> None:
        self._resolver = {}

    def register(self, name: str, func: Callable | Awaitable):
        self._resolver[name] = func

    async def resolve(self, name: str, *args, **kwargs):
        return await self._resolver[name](*args, **kwargs)

class Embeddings:
    def __init__(self,base_url ,model, **kwargs):
        self.client = AsyncOpenAI(base_url=base_url, **kwargs)
        self.model = model

    async def gen(self, text: str):
        return await self.client.embeddings.create(input=text, model=self.model)

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
        messages: list[dict],
        actions: list[EvalInjectAction],
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
                action_vector = await asyncio.gather(*[action.evaluator(accumulated_text) for action in actions])
                for action_index, is_triggered in enumerate(action_vector):  # Iterate over action_vector:

                    if await actions[action_index].evaluator(accumulated_text):
                        current_messages.append({"role": "assistant", "content": accumulated_text})
                        injected_content = await actions[action_index].injector(accumulated_text)
                        current_messages.append({"role": "assistant", "content": injected_content})
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


def BM25Action(query: str, threshold: float = 0.5) -> Callable:
    def decorator(func: Callable[[str], Awaitable[str]]):
        class BM25ActionWrapper(EvalInjectAction):
            def __init__(self, func: Callable[[str], Awaitable[str]]):
                self.func = func
                self.query = query
                self.threshold = threshold

            async def evaluator(self, text: str) -> bool:
                # Simple tokenization (adjust as needed)
                tokenized_text = text.split()
                tokenized_query = self.query.split()
                # Build a BM25 index on a single "document" (the accumulated text)
                bm25 = rank_bm25.BM25L([tokenized_text])
                scores = bm25.get_scores(tokenized_query)
                score = scores[0]
                return score > self.threshold

            async def injector(self, text: str) -> str:
                return await self.func(text)

        return BM25ActionWrapper(func)
    return decorator

# Regex-based decorator
def RegexAction(pattern: str) -> Callable:
    compiled_pattern = re.compile(pattern)
    def decorator(func: Callable[[str], Awaitable[str]]):
        class RegexActionWrapper(EvalInjectAction):
            def __init__(self, func: Callable[[str], Awaitable[str]]):
                self.func = func
                self.pattern = compiled_pattern

            async def evaluator(self, text: str) -> bool:
                return bool(self.pattern.search(text))

            async def injector(self, text: str) -> str:
                return await self.func(text)

        return RegexActionWrapper(func)
    return decorator

def SemanticAction(
    query: str,
    threshold: float = 0.7, embeddings: Embeddings = None,
) -> Callable:
    def decorator(func: Callable[[str], Awaitable[str]]):
        class SemanticActionWrapper(EvalInjectAction):
            def __init__(self, func: Callable[[str], Awaitable[str]]):
                self.func = func
                self.query = query
                self.threshold = threshold
                self.embeddings = embeddings

            def __cosine_similarity(self, a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            async def evaluator(self, text: str) -> bool:
                # Compute embeddings for the fixed query and the accumulated text.
                query_emb = await self.embeddings.gen(self.query)
                text_emb = await self.embeddings.gen(text)
                # Here we assume the response is directly a list of floats.
                sim = self.__cosine_similarity(np.array(query_emb), np.array(text_emb))
                return sim >= self.threshold

            async def injector(self, text: str) -> str:
                return await self.func(text)

        return SemanticActionWrapper(func)
    return decorator



if __name__ == "__main__":
    class MockAction(EvalInjectAction):
        async def evaluator(self, text: str) -> bool:
            return "assistance" in text

        async def injector(self, text: str) -> str:
            return "info: please stop using the word assist"

    @BM25Action("code programming concepts")
    async def mock_func(text: str):
        return "info: you are writing code, use markdown format for annotating only focus on the task"

    async def test_gen_with_evalinject():
        a = EvalInjectLLM("http://localhost:8080/v1", "deepseek-r1:1.5b", api_key="ollama")
        
        messages = [{"role": "user", "content": "hello, can you help me with programming a dependency injector for python?"}]
        actions = [MockAction(), mock_func]
        
        async for content in a.gen_with_evalinject(messages, actions):
            print(content, end="")
    
    asyncio.run(test_gen_with_evalinject())
