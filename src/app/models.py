from pydantic import BaseModel
from typing import List
from datetime import datetime

class Conversation(BaseModel):
    message: str
    timestamp: datetime
    role: str

class RepoRequest(BaseModel):
    repo_url: str
    conversations: List[Conversation]

class IssueRequest(BaseModel):
    repo_url: str
    issue_url: str
    conversation: List[Conversation]