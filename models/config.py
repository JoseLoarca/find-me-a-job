from pydantic import BaseModel


class GoogleSearchQueryConfig(BaseModel):
    keywords: str
    exact_match: bool = True
    sites: list[str] = None
    exclude: list[str] = None
    from_date: str = None
    to_date: str = None


class AppConfig(BaseModel):
    serpapi_apikey: str
    search_config: GoogleSearchQueryConfig
    search_max_pages: int
    gemini_api_key: str | None = None
