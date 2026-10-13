# Real Time Web Search Tool with GenAI

A simple multi-agent research tool. It searches the web, scrapes pages, writes a report and then reviews it.

How it works:
1. Search agent finds recent info on your topic (Tavily)
2. Pages are scraped for detail (BeautifulSoup)
3. Writer chain makes a structured report
4. Critic chain scores the report and gives feedback

## Setup

1. Clone the repo:
```
git clone https://github.com/nitinojha-king/Real_time_web_search_tool_with_genai.git
cd Real_time_web_search_tool_with_genai
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Add your keys:

Copy `.env.example` to `.env` and fill it in:
```
OPENROUTER_API_KEY=your-key
TAVILY_API_KEY=your-key
```

You can get keys from:
- https://openrouter.ai
- https://tavily.com

## Run

```
python pipeline.py
```

Then enter a topic when asked, for example:
```
enter the topic: AI agents in 2026
```

Output has 4 parts: search result, scraped content, final report, critic score.

## Files

- `pipeline.py` - main flow, run this
- `agents.py` - search agent, scrape agent, writer and critic
- `tools.py` - web_search and scrape_url tools
- `requirements.txt` - dependencies

## Notes

- Uses `nvidia/nemotron-3-super-120b-a12b:free` through OpenRouter by default. You can change the model in `agents.py`.
- Tavily free tier is enough for testing.
