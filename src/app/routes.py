from fastapi import APIRouter, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from app import models, functions
from app.dataloaders import analyze_repository, generate_docs_summary, find_issue_context, RepositoryManager
from app.functions import summarize, extract, select, extract_and_summarize

import re
from typing import Optional, Tuple, Union
from urllib.parse import urlparse

router = APIRouter()

@router.post("/sum-repo")
async def get_repo_summary(request: models.RepoRequest):
    if not request.url:
        return
    owner, repo, issue_number = parse_github_url(request.url, request.type)
    # data = await analyze_repository(owner, repo)
    return {"data": "This is a placeholder summary for the repository."}

@router.post("/sum-issue")
async def get_issue_summary(request: models.RepoRequest):
    if not request.url:
        return
    owner, repo, issue_number = parse_github_url(request.url, request.type)
    # data = await find_issue_context(owner, repo, issue_number)
    return {"data": "This is a placeholder summary for the issue."}

@router.post("/fixes")
async def get_fixes(request: models.RepoRequest):
    if not request.url:
        return
    owner, repo, issue_number = parse_github_url(request.url, request.type)
    return {"data": "These are placeholder fixes."}

@router.post("/instructions")
async def instructions(request: models.RepoRequest):
    if not request.url:
        return    
    owner, repo, issue_number = parse_github_url(request.url, request.type)
    return {"data": "These are placeholder instructions."}

@router.post("/chat")
async def chat(request: models.RepoRequest):
    if not request.url:
        return
    owner, repo, issue_number = parse_github_url(request.url, request.type)
    return {"data": "This is a placeholder chat response."}


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
    
    raise ValueError("Invalid GitHub URL format")