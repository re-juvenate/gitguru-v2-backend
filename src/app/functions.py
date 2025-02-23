from goap.llm import EvalInjectLLM, Embeddings, acluster, chunk, SemanticAction, RegexAction, memDB
import asyncio

llm = EvalInjectLLM(f"http://localhost:{PORT_OLLAMA}/v1", f"{LLM_MODEL}", api_key="ollama")
embeddings = Embeddings(f"http://localhost:{PORT_OLLAMA}/v1", f"{EMBED_MODEL}", api_key="ollama")

# Summarization pipeline (Longsum)
async def summarize(objective="", text):
    chunks = chunk(text, "\n")
    clusters = await acluster(chunks, embeddings, min_s=2, max_s=1000)
    cluster_sums = [llm.gen([{"role": "user", "content": f"Summarize the following {objective}, be specific and capture the details: {text}"}]) for text in clusters]
    cluster_sums = await asyncio.gather(*cluster_sums)
    return await llm.gen([{"role": "user", "content": f"Summarize the following {objective}, be specific and capture the details: {' -- '.join(cluster_sums)}"}])

# 
async def extract(objective: str, texts: list[str], *args):
    vecs = await embeddings.gen(texts)
    db = memDB()
    db.extend(texts, vecs)
    top_texts = db.search(objective, 10)
    extra_args = " ".join(args)
    return await llm.gen([{"role": "user", "content": f"Filter and extract the most suitable {objective} for {extra_args} from the following texts: {' -- '.join(top_texts)}"}])

async def extract_and_summarize(objective: str, texts: list[str], *args):
    vecs = await embeddings.gen(texts)
    db = memDB()
    db.extend(texts, vecs)
    top_texts = db.search(objective, 10)
    extra_args = " ".join(args)
    return await summarize(objective+extra_args, await extract(objective, top_texts, *args))












