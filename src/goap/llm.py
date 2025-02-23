from os import name
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
    def __init__(self, name: str):
        self.name = name

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
    
    # async def gen_with_evalinject(
    #     self,
    #     messages: List[dict],
    #     actions: List[EvalInjectAction],  # Updated type hint
    # ) -> AsyncGenerator[str, None]:
    #     current_messages = messages.copy()
    #     accumulated_text = ""  # Track across iterations
    #     current_actions = actions
    #     print("".join(action.name for action in current_actions))
    #     while True:
    #         stream = await self.client.chat.completions.create(
    #             model=self.model,
    #             messages=current_messages+[{"role": "assistant", "content": "Actions (you can use them by talking about them): "}],
    #             stream=True
    #         )
    #         # Reset for new stream
    #         accumulated_text = ""
    #         triggered = False
            
    #         n=0
    #         async for chunk in stream:
    #             content = chunk.choices[0].delta.content or ""
    #             accumulated_text += content
    #             yield content
    #             if n<6:
    #                 n=n+1
    #                 continue
    #             action_results = await asyncio.gather(
    #                 *[action.evaluator(accumulated_text) for action in actions]
    #             )
    #             # print(action_results)
    #             for action_idx, is_triggered in enumerate(action_results):
    #                 triggered = is_triggered
    #                 if is_triggered:
    #                     action = actions[action_idx]
    #                     injected_content = await action.injector(accumulated_text)
    #                     current_messages.extend([
    #                         {"role": "assistant", "content": accumulated_text},
    #                         {"role": "user", "content": injected_content}  # Correct role
    #                     ])
    #                     n = n-1
    #                     print(f"Action triggered: {actions[action_idx].name}")
    #                     break
    #         if triggered:
    #             break

    #         if not triggered:
    #             # Append final assistant response
    #             current_messages.append(
    #                 {"role": "assistant", "content": accumulated_text}
    #             )
    #             break
    #     print(current_messages)

    async def gen_with_evalinject(self,messages: list[dict],actions: List[EvalInjectAction],) -> AsyncGenerator[str, None]:
        current_messages = messages.copy()
        accumulated_text = ""
        
        while True:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=current_messages + [{
                    "role": "assistant", 
                    "content": "Available Actions: " + ", ".join(action.name for action in actions)
                }],
                stream=True
            )
            
            accumulated_text = ""
            triggered = False
            action_triggered = None
            n = 0
            
            async for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                accumulated_text += content
                yield content  # Stream out the response
                if (n := n + 1) % 6 != 0:
                    continue
                action_results = await asyncio.gather(
                    *(action.evaluator(accumulated_text) for action in actions),
                    return_exceptions=True  # Prevent single failure from breaking all
                )
                for action, result in zip(actions, action_results):
                    if isinstance(result, Exception):
                        continue  # Or handle errors as needed
                    if result:
                        action_triggered = action
                        triggered = True
                        break
                    
                if triggered:
                    # Handle the action injection
                    injected_content = await action_triggered.injector(accumulated_text)
                    current_messages.extend([
                        {"role": "assistant", "content": accumulated_text},
                        {"role": "user", "content": injected_content}
                    ])
                    break  # Exit chunk loop for action handling

            if triggered:
                continue  # Restart main loop with updated messages
                
            # Finalize non-triggered completion
            current_messages.append({
                "role": "assistant", 
                "content": accumulated_text
            })
            break

        print("Final message chain:", current_messages)

class BaseActionWrapper(EvalInjectAction):
    """Base class for action wrappers to reduce code duplication"""
    def __init__(self, func: Callable[[str], Awaitable[str]]):
        super().__init__(name="")
        self.func = func

    async def injector(self, text: str) -> str:
        """Default injector implementation shared by all actions"""
        return await self.func(text)

def BM25Action(name: str, query: str, threshold: float = 0.5):
    """Decorator for BM25-based content evaluation"""
    def decorator(func: Callable[[str], Awaitable[str]]):
        class BM25ActionWrapper(BaseActionWrapper):
            def __init__(self, func: Callable[[str], Awaitable[str]]):
                super().__init__(func)
                self.name = name
                self.query_tokens = query.split()
                self.threshold = threshold

            async def evaluator(self, text: str) -> bool:
                """Evaluate using BM25 ranking"""
                text_tokens = text.lower().split()
                
                if not text_tokens:
                    return False
                
                bm25 = rank_bm25.BM25L([text_tokens])
                return max(bm25.get_scores(self.query_tokens)) > self.threshold

        return BM25ActionWrapper(func)
    return decorator

def RegexAction(name: str, pattern: str):
    """Decorator for regex-based content evaluation"""
    compiled = re.compile(pattern)
    
    def decorator(func: Callable[[str], Awaitable[str]]):
        class RegexActionWrapper(BaseActionWrapper):
            def __init__(self, func: Callable[[str], Awaitable[str]]):
                super().__init__(func)
                self.name = name
                self.pattern = compiled

            async def evaluator(self, text: str) -> bool:
                """Check for pattern match"""
                return bool(self.pattern.search(text))

        return RegexActionWrapper(func)
    return decorator

def SemanticAction(name:str, 
    query: str,
    threshold: float = 0.9,
    *,  # Force keyword-only args after this point
    embeddings: Embeddings  # Required parameter
) :
    def decorator(func: Callable[[str], Awaitable[str]]):
        class SemanticActionWrapper(BaseActionWrapper):
            def __init__(self, func: Callable[[str], Awaitable[str]]):
                super().__init__(func)
                self.name = name
                self.query = query
                self.threshold = threshold
                self.embeddings = embeddings
                self._query_embedding = None

            async def _get_query_embedding(self) -> list[float]:
                if not self._query_embedding:
                    emb = await self.embeddings.gen([self.query])
                    self._query_embedding = emb[0]
                return self._query_embedding

            def _cosine_sim(self, a: list[float], b: list[float]) -> float:
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            async def evaluator(self, text: str) -> bool:
                q_embed = await self._get_query_embedding()
                t_embed = (await self.embeddings.gen([text]))[0]
                similarity = self._cosine_sim(q_embed, t_embed)
                return similarity >= self.threshold

        return SemanticActionWrapper(func)
    return decorator

if __name__ == "__main__":

    @BM25Action("stop_helping", "fuck you hate retard")
    async def stop_helping(text: str):
        return "info: please stop using the word assist"


    async def test_gen_with_evalinject():
        a = EvalInjectLLM("http://localhost:8081/v1", "deepseek-r1:1.5b", api_key="ollama")
        e = Embeddings("http://localhost:8080/v1", "Snowflake Arctic Embed M", api_key="ollama")
        
        @SemanticAction("code_formatting", query="code programming format ```", embeddings=e)
        async def mock_func(text: str):
            print(text)
            return "info: you are writing code, use markdown format for annotating only focus on the task"

        messages = [{"role": "user", "content": "hello, can you help me with programming a dependency injector for python? Also fuck you"}]
        actions = [stop_helping, mock_func]
        
        async for content in a.gen_with_evalinject(messages, actions):
            print(content, end="")
    
    asyncio.run(test_gen_with_evalinject())
