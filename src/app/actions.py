from __future__ import annotations
from dotenv import load_dotenv
import os
import aiohttp
import re
import base64
import subprocess
from typing import List, Dict, Any, Optional
import asyncio
import getpass

# Configuration Constants
GITHUB_API_VERSION = "2022-11-28"
BASE_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": GITHUB_API_VERSION
}

def get_github_token() -> str:
    if "GITHUB_API_KEY" not in os.environ:
        os.environ["GITHUB_API_KEY"] = getpass.getpass("GitHub API Key:")
    return os.environ["GITHUB_API_KEY"]

# Core GitHub Client
class GitHubClient:
    def __init__(self):
        self.token = get_github_token()
        self.headers = {**BASE_HEADERS, "Authorization": f"Bearer {self.token}"}
    
    async def fetch(self, url: str) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()

# Repository Operations
class RepositoryManager(GitHubClient):
    async def get_filetree(self, owner: str, repo: str, branch: str = "main") -> List[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        data = await self.fetch(url)
        return [item["path"] for item in data.get("tree", [])]

    async def get_readme(self, owner: str, repo: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        data = await self.fetch(url)
        return base64.b64decode(data["content"]).decode("utf-8")

    async def get_file_content(self, owner: str, repo: str, path: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        data = await self.fetch(url)
        return base64.b64decode(data["content"]).decode("utf-8")

    async def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        return await self.fetch(url)

# Issue Operations
class IssueManager(GitHubClient):
    async def get_issue(self, owner: str, repo: str, number: int) -> Dict:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
        return await self.fetch(url)

    async def get_issue_comments(self, owner: str, repo: str, number: int) -> List[Dict]:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments"
        return await self.fetch(url)

    async def full_issue_thread(self, owner: str, repo: str, number: int) -> List[str]:
        issue = await self.get_issue(owner, repo, number)
        comments = await self.get_issue_comments(owner, repo, number)
        return [
            f"{issue['title']}\n{issue['body']}",
            *[f"@{c['user']['login']}: {c['body']}" for c in comments]
        ]

# Analysis Utilities
class RepoAnalyzer:
    @staticmethod
    def filter_text_files(paths: List[str]) -> List[str]:
        return [p for p in paths if p.endswith((".md", ".rst")) or p.lower().startswith("readme")]

    @staticmethod
    def filter_files(paths: List[str], *ext: str) -> List[str]:
        return [p for p in paths if p.endswith(ext)]
    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        return re.findall(r'```[\s\S]*?```', text)

# Feature Pipelines
async def analyze_repository(owner: str, repo: str) -> Dict[str, Any]:
    repo_mgr = RepositoryManager()
    return {
        "structure": await repo_mgr.get_filetree(owner, repo),
        "readme": await repo_mgr.get_readme(owner, repo),
        "languages": await repo_mgr.get_languages(owner, repo),
        "documentation": RepoAnalyzer.filter_text_files(await repo_mgr.get_filetree(owner, repo))
    }

async def generate_docs_summary(owner: str, repo: str) -> str:
    repo_mgr = RepositoryManager()
    readme = await repo_mgr.get_readme(owner, repo)
    files = RepoAnalyzer.filter_text_files(await repo_mgr.get_filetree(owner, repo))
    files= files[:10]
    contents = [readme] + [await repo_mgr.get_file_content(owner, repo, p) for p in files]
    return "\n\n".join(contents)

async def find_issue_context(owner: str, repo: str, issue_number: int) -> Dict:
    issue_mgr = IssueManager()
    repo_mgr = RepositoryManager()
    
    thread = await issue_mgr.full_issue_thread(owner, repo, issue_number)
    code_blocks = [b for msg in thread for b in RepoAnalyzer.extract_code_blocks(msg)]
    files = await repo_mgr.get_filetree(owner, repo)
    
    return {
        "conversation": thread,
        "code_blocks": code_blocks,
        "related_files": files  # Add semantic matching here
    }



# Execution
if __name__ == "__main__":
    async def main():
        owner, repo = "python", "cpython"
        
        # Example analysis
        analysis = await analyze_repository(owner, repo)
        print(f"Repo contains {len(analysis['structure'])} files")
        print(f"Top language: {max(analysis['languages'], key=analysis['languages'].get)}")
        print(f"Documentation files: {len(analysis['documentation'])}")
        
        # Clone repository
        # subprocess.run(["git", "clone", f"https://github.com/{owner}/{repo}.git"], check=True)

    asyncio.run(main())