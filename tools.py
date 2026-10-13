from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY") or "missing-key")
  
@tool
def web_search(query: str) -> str:
    """
    Perform a web search using Tavily API and return the top result.
    """
    if not query or not query.strip():
        return "Web search failed: query must not be empty."
    if not os.getenv("TAVILY_API_KEY"):
        return "Web search failed: TAVILY_API_KEY is not set."
    try:
        response = tavily.search(query=query.strip(), max_results=5)
    except Exception as e:
        return f"Web search failed: {str(e)}"
    results = response.get('results', []) if isinstance(response, dict) else []
    if not results:
        return "No search results found."
    out = []
    for result in results:
        title = result.get('title', '')
        url = result.get('url', '')
        snippet = result.get('content', result.get('snippet', ''))
        out.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n")

    return "\n".join(out)
 

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading. Pass a single URL."""
    url = (url or "").strip().strip("'\"")
    if not url.startswith(("http://", "https://")):
        return f"Could not scrape URL {url}: URL must start with http:// or https://"
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        if not text:
            return f"No readable text found at URL: {url}"
        return text[:3000]
    except Exception as e:
        return f"Could not scrape URL {url}: {str(e)}"