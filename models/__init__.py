from pydantic import BaseModel


class GoogleSearchResult(BaseModel):
    session_id: str
    search_id: list[str]
    query: str


class GoogleSearchOrganicResult(BaseModel):
    position: int
    title: str
    link: str
    snippet: str
    source: str
