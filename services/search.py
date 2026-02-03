from uuid import uuid4

import serpapi


def _build_search_query(keywords: str, exact_match: bool = True, sites: list[str] = None, exclude: list[str] = None,
                        from_date: str = None, to_date: str = None):
    """Build the query for the Google Search to be performed.

    Args:
        keywords: main keywords to be looked up
        exact_match: if this is True, then we add quotes to the keywords to get an exact match from Google
        sites: list of sites to search
        exclude: list of keywords to exclude from our search
        from_date: starting date
        to_date: end date

    Returns: a string with a Google-friendly search query

    """
    normalized_keywords = keywords.strip('"').lower()
    keywords_query = f'"{normalized_keywords}"' if exact_match else normalized_keywords

    exclude_query = " ".join([f'-"{exclusion}"' for exclusion in exclude])

    if sites:
        sites_query = "(" + " OR ".join([f'site:{site}' for site in sites]) + ")"
    else:
        sites_query = ""

    from_query = f'before:{from_date}' if from_date else ""
    to_query = f'before:{to_date}' if to_date else ""

    return f'{keywords_query} {exclude_query} {sites_query} {from_query} {to_query}'.strip()


class JobSearch:
    """Handles Google search via SerpAPI"""

    def __init__(self, api_key: str):
        self.client = serpapi.Client(api_key=api_key)
        self.session_id = uuid4()
        self.engine = "google"
        self.location = "United States"
        self.google_domain = "google.com"
        self.gl = "us"
        self.hl = "en"

    def execute_search(self, search_query: str, max_pages: int = 3):
        """Executes a Google Search with a given search query

        Args:
            search_query: search query to be used
            max_pages: pagination

        Returns:
            dict with search metadata and search results
        """
        params = self._get_search_params(search_query)

        # Initialize a search
        search = self.client.search(**params)

        organic_results = []
        search_ids = []
        for page in search.yield_pages(max_pages=max_pages):
            search_ids.append(page["search_metadata"]["id"])
            organic_results.append(page["organic_results"])

        return {"session_id": self.session_id, "total_pages": len(organic_results), "organic_results": organic_results}

    def _get_search_params(self, search_query: str):
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
