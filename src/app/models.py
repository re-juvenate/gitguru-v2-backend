from pydantic import BaseModel
from typing import List
from datetime import datetime
from typing import Literal

class Conversation(BaseModel):
    message: str
    timestamp: datetime
    role: str

class RepoRequest(BaseModel):
    url: str
    type: Literal["repo", "issue"]
    conversations: List[Conversation]

# class IssueRequest(BaseModel):
#     repo_url: str
#     issue_url: str
#     conversation: List[Conversation]