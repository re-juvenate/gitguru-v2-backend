from dotenv import load_dotenv
import os
import aiohttp
import asyncio
import getpass

from goap.llm import SemanticAction, EvalInjectLLM, Embeddings, Resolver

load_dotenv()


llm = EvalInjectLLM()

 

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
