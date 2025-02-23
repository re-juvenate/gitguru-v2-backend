from fastapi import APIRouter, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from app import models, functions
from app.dataloaders import analyze_repository, generate_docs_summary, find_issue_context, RepositoryManager
from app.functions import summarize, extract, select, extract_and_summarize

router = APIRouter()

@router.post("/sum-repo")
async def get_repo_summary(request: models.RepoRequest):
    owner, repo = url_parser(request.repo_url)
    # data = await analyze_repository(owner, repo)
    return {"data": "This is a placeholder summary for the repository."}

@router.post("/sum-issue")
async def get_issue_summary(request: models.RepoRequest):
    owner, repo, issue_number = url_parser(request.issue_url)
    # data = await find_issue_context(owner, repo, issue_number)
    return {"data": "This is a placeholder summary for the issue."}

@router.post("/fixes")
async def get_fixes(request: models.RepoRequest):
    owner, repo, issue_number = url_parser(request.issue_url)
    return {"data": "These are placeholder fixes."}

@router.post("/instructions")
async def instructions(request: models.RepoRequest):
    owner, repo = url_parser(request.repo_url)
    return {"data": "These are placeholder instructions."}

@router.post("/chat")
async def chat(request: models.RepoRequest):
    owner, repo, issue_number = url_parser(request.repo_url)
    return {"data": "This is a placeholder chat response."}

def url_parser(url):
    url = url.split("/")
    owner = url[3]
    repo = url[4]
    try:
        issue_number = url[6]
        return (owner, repo, issue_number)
    except:
        return (owner, repo)