from pydantic import BaseModel


class GoogleSearchResult(BaseModel):
    session_id: str
    id: str
    status: str
    processed_at: str
    query: str


class GoogleSearchOrganicResult(BaseModel):
    position: int
    title: str
    link: str
    snippet: str
    source: str
