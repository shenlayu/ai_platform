import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from serpapi import BingSearch

def search(content: str) -> str:
    params = {
        "engine": "bing",
        "q": "Coffee",
        "cc": "US",
        "api_key": "775cd6dcce704bc414b64fe3afd11995cf2529841f84829e26c7c1f5bdca083a"
    }
    search = BingSearch(params)
    search_results = search.get_dict()
    
    if search_results and "organic_results" in search_results:
        snippet = search_results["organic_results"][0]["snippet"]
        combined_content = f"Please answer '{content}' based on the search result:\n\n{snippet}"
        return combined_content
    else:
        return f"Sorry, I couldn't find any results for '{content}'."

if __name__ == "__main__":
    print(search("Who is Sun Wukong?"))
