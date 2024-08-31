import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

def search(content: str) -> str:
    params = {
        "engine": "bing",
        "q": "Coffee",
        "cc": "US",
        "api_key": "948b3291d28c07eac5fbb7f0b49a69b5a51a1c0e24f53d5840562034666c9ad3"
    }
    search = GoogleSearch(params)
    search_results = search.get_dict()
    
    if search_results and "organic_results" in search_results:
        snippet = search_results["organic_results"][0]["snippet"]
        combined_content = f"Please answer '{content}' based on the search result:\n\n{snippet}"
        return combined_content
    else:
        return f"Sorry, I couldn't find any results for '{content}'."

if __name__ == "__main__":
    print(search("Who is Sun Wukong?"))
