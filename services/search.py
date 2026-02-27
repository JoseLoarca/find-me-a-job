from uuid import uuid4

import serpapi

from models import GoogleSearchQueryConfig


def _build_search_query(query_config: GoogleSearchQueryConfig) -> str:
    """Build the query for the Google Search to be performed.

    Args:
        query_config: a GoogleSearchQueryConfig object containing the configurations (keywords, sites, exclusions, etc.)
         for the Google Search to be  performed

    Returns: a string with a Google-friendly search query

    """
    normalized_keywords = query_config.keywords.strip('"').lower()
    keywords_query = f'"{normalized_keywords}"' if query_config.exact_match else normalized_keywords

    exclude_query = " ".join([f'-"{exclusion}"' for exclusion in query_config.exclude])

    if query_config.sites:
        sites_query = "(" + " OR ".join([f'site:{site}' for site in query_config.sites]) + ")"
    else:
        sites_query = ""

    from_query = f'after:{query_config.from_date}' if query_config.from_date else ""
    to_query = f'before:{query_config.to_date}' if query_config.to_date else ""

    return f'{keywords_query} {exclude_query} {sites_query} {from_query} {to_query}'.strip()


class JobSearch:
    """Handles Google search via SerpAPI"""

    def __init__(self, api_key: str):
        self.client = serpapi.Client(api_key=api_key)
        self.session_id = str(uuid4())
        self.engine = "google"
        self.location = "United States"
        self.google_domain = "google.com"
        self.gl = "us"
        self.hl = "en"

    def execute_search(self, query_config: GoogleSearchQueryConfig, max_pages: int = 3) -> dict:
        """Executes a Google Search with a given search query

        Args:
            query_config: a GoogleSearchQueryConfig object containing the configurations (keywords, sites, exclusions,
                etc.) for the Google Search to be  performed
            max_pages: pagination

        Returns:
            dict with search metadata and search results
        """
        search_query = _build_search_query(query_config)
        params = self._get_search_params(search_query)

        # Initialize a search
        search = self.client.search(**params)

        organic_results = []
        search_ids = []
        for page in search.yield_pages(max_pages=max_pages):
            search_ids.append(page["search_metadata"]["id"])
            organic_results.extend(page["organic_results"])

        return {"session_id": self.session_id,
                "search_ids": search_ids,
                "query": search_query,
                "total_pages": int(len(organic_results) / max_pages),
                "organic_results": organic_results}

    def _get_search_params(self, search_query: str) -> dict:
        """Formats the params for a Google Search

        Args:
            search_query: search query to be used

        Returns:
            dict with the params for a Google Search
        """
        return {
            "engine": self.engine,
            "q": search_query,
            "location": self.location,
            "google_domain": self.google_domain,
            "gl": self.gl,
            "hl": self.hl,
        }
