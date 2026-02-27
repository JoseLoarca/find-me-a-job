from pydantic import BaseModel


class GoogleSearchMetadata(BaseModel):
    session_id: str
    search_ids: list[str]
    query: str
    total_pages: int


class GoogleSearchOrganicResult(BaseModel):
    position: int
    title: str
    link: str
    snippet: str
    source: str
    job_id: str