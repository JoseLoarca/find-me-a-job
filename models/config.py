from pydantic import BaseModel


class GoogleSearchQueryConfig(BaseModel):
    keywords: str
    exact_match: bool = True
    sites: list[str] = None
    exclude: list[str] = None
    from_date: str = None
    to_date: str = None


class AppConfig(BaseModel):
    # Search config
    serpapi_apikey: str
    search_config: GoogleSearchQueryConfig
    search_max_pages: int

    # Services
    storage_service: str = "mongodb"
    analyzer_service: str | None = "gemini"
    evaluator_service: str | None = "gemini"

    # Service specific configuration fields
    gemini_api_key: str | None = None
    mongodb_uri: str | None = None
    mongodb_dbname: str | None = None