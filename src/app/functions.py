from goap.llm import EvalInjectLLM, Embeddings, acluster, chunk, SemanticAction, RegexAction, memDB
from sast.semgrep import SemgrepScanner
from sast.searxng import SearxngSearch
import asyncio
import tempfile
import aiofiles
from dotenv import load_dotenv
import os

load_dotenv()

PORT_OLLAMA=os.environ["PORT_OLLAMA"]
LLM_MODEL=os.environ["LLM_MODEL"]
EMBED_MODEL=os.environ["EMBED_MODEL"]

llm = EvalInjectLLM(f"http://ollama:11434/v1", f"{LLM_MODEL}", api_key="ollama")
embeddings = Embeddings(f"http://ollama:11434/v1", f"{EMBED_MODEL}", api_key="ollama")

# Summarization pipeline (Longsum)
async def summarize(objective="", text=""):
    if not text:
        return
    chunks = chunk(text, "\n")
    clusters = await acluster(chunks, embeddings, min_s=2, max_s=1000)
    cluster_sums = [llm.gen([{"role": "user", "content": f"Summarize the following {objective}, be specific and capture the details: {text}"}]) for text in clusters]
    cluster_sums = await asyncio.gather(*cluster_sums)
    return await llm.gen([{"role": "user", "content": f"Summarize the following {objective}, be specific and capture the details: {' -- '.join(cluster_sums)}"}])

async def filter_vec(texts: list[str], objective: str, k=10):
    vecs = await embeddings.gen(texts)
    db = memDB()
    db.extend(texts, vecs)
    top_texts = db.search(objective, k)
    return top_texts

async def extract(objective: str, texts: list[str], *args):
    top_texts = await filter_vec(texts, objective)
    extra_args = " ".join(args)
    return await llm.gen([{"role": "user", "content": f"Filter and extract the most suitable {objective} for {extra_args} from the following texts: {' -- '.join(top_texts)}"}])

async def extract_and_summarize(objective: str, texts: list[str], *args):
    vecs = await embeddings.gen(texts)
    db = memDB()
    db.extend(texts, vecs)
    top_texts = db.search(objective, 10)
    extra_args = " ".join(args)
    return await summarize(objective+extra_args, await extract(objective, top_texts, *args))

async def select(texts: list[str], *args):
    extra_args = " ".join(args)
    top_texts = await filter_vec(texts, extra_args)
    top_text_reasoning = [llm.gen([{"role": "user", "content": f"Tell me why {text} would be a good {extra_args}"}]) for text in top_texts]
    top_text_reasoning = await asyncio.gather(*top_text_reasoning)
    mapping = dict(zip(top_text_reasoning, top_texts))
    top_texts_by_reasoning = await filter_vec(top_text_reasoning, extra_args)
    return mapping[top_texts_by_reasoning[0]]


async def save_to_tempfile(data: str) -> str:
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    temp_file.close()

    # Write data to the temporary file asynchronously
    async with aiofiles.open(temp_file_path, mode='w') as file:
        await file.write(data)

    return temp_file_path

