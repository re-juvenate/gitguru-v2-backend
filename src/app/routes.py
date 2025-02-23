from fastapi import APIRouter, HTTPException
from app import models, functions
from app.dataloaders import IssueManager, analyze_repository, generate_docs_summary, find_issue_context, RepositoryManager
from app.functions import summarize, extract, select, extract_and_summarize
from goap.llm import EvalInjectLLM, Embeddings, SemanticAction, RegexAction
from sast.semgrep import SemgrepScanner
from sast.searxng import SearxngSearch
import asyncio
import re
from urllib.parse import urlparse
from typing import Tuple, Union


router = APIRouter()

llm = functions.llm
embeddings = functions.embeddings

@router.post("/sum-repo")
async def get_repo_summary(request: models.RepoRequest):
    """Generate comprehensive repository summary including structure, docs, and languages"""
    try:
        owner, repo, _ = parse_github_url(request.url, request.type)
        analysis = await analyze_repository(owner, repo)
        context = f"""
        Repository Structure: {', '.join(analysis['structure'][:10])}... ({len(analysis['structure'])} files total)
        Main Languages: {', '.join(analysis['languages'].keys())}
        Documentation: {len(analysis['documentation'])} files
        """
        return {"data": await summarize("repository overview", context + analysis["readme"])}
    except Exception as e:
        raise HTTPException(500, f"Repo analysis failed: {str(e)}")

@router.post("/sum-issue")
async def get_issue_summary(request: models.RepoRequest):
    """Condense issue thread with code context and related files"""
    try:
        owner, repo, issue_number = parse_github_url(request.url, request.type)
        if not issue_number:
            raise ValueError("Invalid issue URL")
            
        data = await find_issue_context(owner, repo, int(issue_number))
        combined = [
            "ISSUE DISCUSSION:\n",data["conversation"],
            "RELEVANT CODE:\n" , data["code_blocks"][:3]
        ]
        return {"data": await extract_and_summarize(
            "technical issue context", 
            combined,
            "Include reproduction steps, error messages, and proposed solutions"
        )}
    except Exception as e:
        raise HTTPException(500, f"Issue summary failed: {str(e)}")

@router.post("/fixes")
async def get_fixes(request: models.RepoRequest):
    """Suggest code fixes with file references"""
    try:
        owner, repo, issue_number = parse_github_url(request.url, request.type)
        data = await find_issue_context(owner, repo, int(issue_number))
        
        if not data["code_blocks"]:
            return {"data": "No code samples found in issue"}
            
        # Get most relevant files for the code samples
        selected_files = await select(
            data["related_files"], data["code_blocks"], "code files needing fixes",
        )
        
        # Get actual file contents
        repo_mgr = RepositoryManager()
        file_contents = await asyncio.gather(*[
            repo_mgr.get_file_content(owner, repo, f)
            for f in selected_files[:3]  # Top 3 files
        ])
        
        return {"data": await extract(
            "potential code fixes",
            file_contents + data["code_blocks"],
            "Suggest concrete code changes with explanations"
        )}
    except Exception as e:
        raise HTTPException(500, f"Fix generation failed: {str(e)}")

@router.post("/instructions")
async def instructions(request: models.RepoRequest):
    """Generate setup/contribution instructions from docs"""
    try:
        owner, repo, _ = parse_github_url(request.url, request.type)
        docs = await generate_docs_summary(owner, repo)
        return {"data": await extract(
            "setup and usage instructions", 
            docs.split("\n\n"),
            "Include installation, configuration, and basic usage steps"
        )}
    except Exception as e:
        raise HTTPException(500, f"Instruction extraction failed: {str(e)}")

@router.post("/chat")
async def chat(request: models.RepoRequest):
    """AI assistant with repo-aware knowledge"""
    try:
        owner, repo, issue_number = parse_github_url(request.url, request.type)
        context = ""

        # @SemanticAction("search", query="search, research, look it up", embeddings=embeddings)
        # async def search(query: str):
        #     """Web search integration"""
        #     return "\n".join([
        #         f"{r['title']}: {r['snippet']}"
        #         for r in await SearxngSearch(f"{repo} how to fix {IssueManager().get_issue(owner, repo, issue_number)}")
        #     ])

        # @SemanticAction("docs", query="documentation, readme", embeddings=embeddings)
        # async def get_docs(query: str):
        #     """Repo documentation lookup"""
        #     return await summarize("documentation", await generate_docs_summary(owner, repo))

        # if issue_number:
        #     issue_data = await find_issue_context(owner, repo, int(issue_number))
        #     context += f"\nISSUE CONTEXT:\n{await summarize('active issue', issue_data['conversation'])}"

        # return {"data": await llm.gen([{
        #     "role": "user",
        #     "content": f"{request}\n\nREPO CONTEXT:{context}"
        # }])}
    except Exception as e:
        raise HTTPException(500, f"Chat failed: {str(e)}")

def parse_github_url(url: str, type: str) -> Tuple[str, str, int]:

    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')

    if type == 'repo' and len(path_parts) >= 2:
        owner, repo_name = path_parts[:2]
        return owner, repo_name, 0  # Default value for issue_number

    if type == 'issue' and len(path_parts) >= 4 and path_parts[2] == 'issues' and path_parts[3].isdigit():
        owner, repo_name = path_parts[:2]
        issue_id = int(path_parts[3])
        return owner, repo_name, issue_id

    raise ValueError("Invalid GitHub URL format or type")