@dataclass
class RepoCtx:
    repo: str = repo_url

class ChatCtx:
    chatcontext: list[{"role": "message"}]
    message: str

class Summarise:
    repo: str = repo_url
