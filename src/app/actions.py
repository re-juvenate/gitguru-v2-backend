from dotenv import load_dotenv
import os
import aiohttp
import asyncio
import getpass

from goap.llm import SemanticAction, EvalInjectLLM, Embeddings, Resolver

load_dotenv()


llm = EvalInjectLLM()

# to generate llm response await llm.gen(messages)

 

if "GITHUB_API_KEY" not in os.environ:
    os.environ["GITHUB_API_KEY"] = getpass.getpass("Github API Key:")
token = os.environ["GITHUB_API_KEY"]

async def get_issue_body(owner, repo, issue_number):
    global token

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return "Failed to retrieve issue body."
            data = await response.json()
            return data["title"] + "\n" + data["body"]

async def get_issue_comment(owner, repo, issue_number):
    global token

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return ["Failed to retrieve issue comments"]
            body = await get_issue_body(owner, repo, issue_number)
            comments = await response.json()
            comment_list = [body]
            for comment in comments:
                comment_list.append("@" + comment["user"]["login"] + "> " + comment["body"])
            return comment_list

async def get_repo_readme(owner, repo, issue_number=0):
    global token

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return "Failed to retrieve README."
            data = await response.json()
            readme_enc = data["content"]
            readme = base64.b64decode(readme_enc).decode("utf-8")
            return readme

async def get_repo_file(owner, repo, path=""):
    global token

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return "Failed to retrieve file contents."
            data = await response.json()
            return data["content"]

async def get_repo_filetree(owner, repo, issue_number=0):
    global token

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return "Failed to retrieve issue body."
            data = await response.json()
            filetree = data["tree"]
            req_path = [item["path"] for item in filetree if item["type"] != "blob"]
            return req_path

async def get_repo_language(owner, repo, issue_number=0):
    global token

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return ["Failed to retrieve languages."]
            data = await response.json()
            return data

import base64
import re
from typing import List, Dict
import subprocess

# Helper Functions
# ----------------
def filter_text_files(file_paths: List[str]) -> List[str]:
    """Filter markdown/rst files and README"""
    return [
        path for path in file_paths
        if path.endswith((".md", ".rst")) or path.lower() in ["readme", "readme.md"]
    ]

def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from text using regex"""
    return re.findall(r'```[\s\S]*?```', text)

# Feature Pipelines
# -----------------
async def repo_docs_summary(owner: str, repo: str) -> str:
    """Get all documentation content"""
    readme = await get_repo_readme(owner, repo)
    filetree = await get_repo_filetree(owner, repo)
    doc_files = filter_text_files(filetree)
    
    # Fetch all documentation files
    docs = [readme]
    for path in doc_files:
        content = await get_repo_file(owner, repo, path)
        docs.append(f"\n\n## File: {path} ##\n{content}")
    
    return "\n".join(docs)

async def issue_thread_summary(owner: str, repo: str, issue_number: int) -> List[str]:
    """Get complete issue discussion thread"""
    return await get_issue_comment(owner, repo, issue_number)

async def issue_code_extraction(owner: str, repo: str, issue_number: int) -> List[str]:
    """Get code blocks from an issue thread"""
    comments = await get_issue_comment(owner, repo, issue_number)
    return [block for comment in comments for block in extract_code_blocks(comment)]

async def repo_structure_analysis(owner: str, repo: str) -> Dict:
    """Explain repository structure"""
    return {
        "file_tree": await get_repo_filetree(owner, repo),
        "languages": await get_repo_language(owner, repo)
    }

async def issue_relevant_files(owner: str, repo: str, issue_number: int) -> Dict:
    """Find files relevant to an issue"""
    issue_text = "\n".join(await get_issue_comment(owner, repo, issue_number))
    all_files = await get_repo_filetree(owner, repo)
    
    # Simple keyword matching (replace with semantic search in real implementation)
    relevant = []
    for path in all_files:
        if re.search(r'\b' + re.escape(path) + r'\b', issue_text, re.IGNORECASE):
            content = await get_repo_file(owner, repo, path)
            relevant.append({"path": path, "content": content})
    
    return {"issue": issue_text, "relevant_files": relevant}

def clone_repo(owner: str, repo: str, target_dir: str = ".") -> None:
    """Clone repository using git command"""
    subprocess.run(["git", "clone", f"https://github.com/{owner}/{repo}.git", target_dir], check=True)

# Modified Filetree Function
# --------------------------
async def get_repo_filetree(owner: str, repo: str) -> List[str]:
    """Get ALL file paths (including blobs)"""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return [item["path"] for item in data["tree"]]

# Usage Example
# -------------
async def main():
    owner = "python"
    repo = "cpython"
    
    # Example: Get documentation summary
    docs = await repo_docs_summary(owner, repo)
    print(f"Documentation Summary ({len(docs)} chars)")
    
    # Example: Process issue #12345
    issue_num = 12345
    code_blocks = await issue_code_extraction(owner, repo, issue_num)
    print(f"Found {len(code_blocks)} code blocks in issue")
    
    # Clone repo to local
    clone_repo(owner, repo)

if __name__ == "__main__":
    asyncio.run(main())