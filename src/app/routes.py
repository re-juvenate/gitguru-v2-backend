from fastapi import APIRouter, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from app import models, functions

router = APIRouter()

@router.post("/summary")
async def get_summary(request: models.RepoRequest):

    return {"result": "This is a placeholder summary."}

@router.post("/fixes")
async def get_fixes(request: models.RepoRequest):

    return {"result": "These are placeholder fixes."}