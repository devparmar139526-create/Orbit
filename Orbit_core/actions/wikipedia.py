"""
Wikipedia search and information retrieval
"""

import requests
from typing import Optional

class WikipediaAction:
    def __init__(self, settings=None):
        if settings:
            self.api_url = settings.WIKIPEDIA_API_URL
            self.language = settings.WIKIPEDIA_LANGUAGE
            self.default_sentences = settings.WIKIPEDIA_SUMMARY_SENTENCES
        else:
            self.api_url = "https://en.wikipedia.org/w/api.php"
            self.language = "en"
            self.default_sentences = 3

    def search(self, query: str, sentences: int = None) -> str:
        if sentences is None:
            sentences = self.default_sentences
        headers = {
            'User-Agent': 'orbit-AI-Assistant/1.0'
        }
        
        try:
            search_params = {
                "action": "query", "list": "search", "srsearch": query,
                "format": "json", "utf8": 1
            }
            response = requests.get(self.api_url, params=search_params, timeout=10, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            if not search_results:
                return f"I couldn't find any Wikipedia articles about '{query}'."
            
            page_title = search_results[0]["title"]
            
            summary_params = {
                "action": "query", "prop": "extracts", "exintro": True,
                "explaintext": True, "titles": page_title, "format": "json", "utf8": 1
            }
            response = requests.get(self.api_url, params=summary_params, timeout=10, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            page = next(iter(data.get("query", {}).get("pages", {}).values()))
            extract = page.get("extract", "")
            
            if not extract:
                return f"I found a Wikipedia page for '{page_title}', but couldn't retrieve the summary."
            
            sentences_list = extract.split('. ')
            summary = '. '.join(sentences_list[:sentences]) + '.'
            
            return f"According to Wikipedia: {summary}"
        
        except requests.exceptions.RequestException as e:
            return f"Cannot connect to Wikipedia. Please check your internet connection. Error: {e}"
        except Exception as e:
            return f"An unexpected error occurred while searching Wikipedia: {str(e)}"

    def get_full_article(self, title: str) -> Optional[str]:
        # This method is not used by the main loop but is kept for utility
        try:
            params = {
                "action": "query", "prop": "extracts", "explaintext": True,
                "titles": title, "format": "json"
            }
            response = requests.get(self.api_url, params=params, timeout=10)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()))
            return page.get("extract", None)
        except Exception as e:
            print(f"Error fetching full article: {e}")
            return None