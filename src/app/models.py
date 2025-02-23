from pydantic import BaseModel
from typing import List
from datetime import datetime

class Conversation(BaseModel):
    message: str
    date_time: datetime
    role: str

class RepoRequest(BaseModel):
    repo_url: str
    conversations: List[Conversation]