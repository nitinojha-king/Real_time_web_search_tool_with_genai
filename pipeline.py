import re
from agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain
from tools import scrape_url
from dotenv import load_dotenv

load_dotenv()


def _last_text(result: dict) -> str:
    """Extract text from the last agent message, handling str/list content."""
    msg = result["messages"][-1]
    content = msg.content if hasattr(msg, "content") else msg["content"]
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return " ".join(parts).strip()
    return str(content or "").strip()


def _extract_urls(text: str, limit: int = 3) -> list[str]:
    urls = re.findall(r"https?://[^\s\]\)'\"<>]+", text or "")
    seen: list[str] = []
    for u in urls:
        u = u.rstrip(".,;:")
        if u not in seen:
            seen.append(u)
        if len(seen) >= limit:
            break
    return seen


def run_research_pipeline(topic: str) -> dict:
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("Topic must not be empty.")
    state = {}

    # search agent
    print("\n" + "=" * 50 + "\n")
    print("step-1 - search agent is running")

    search_agent = build_search_agent()
    search_result = search_agent.invoke(
        {"messages": [("user", f"find recent, reliable and detailed info about {topic}")]}
    )
    state["search_result"] = _last_text(search_result)
    if not state["search_result"]:
        raise RuntimeError("Search agent returned empty content.")

    print("\nsearch result", state["search_result"])

    # scrape: extract URLs in code, scrape directly (reliable).
    # Fall back to scrape agent only if no URLs found.
    print("\n" + "=" * 50 + "\n")
    print("step-2 - scraping urls")

    urls = _extract_urls(state["search_result"], limit=3)
    if urls:
        scraped_parts = []
        for u in urls:
            try:
                text = scrape_url.invoke({"url": u})
            except Exception as e:
                text = f"Could not scrape URL {u}: {e}"
            scraped_parts.append(f"SOURCE: {u}\n{text}")
        state["scrape_result"] = "\n\n".join(scraped_parts)
    else:
        scrape_agent = build_scrape_agent()
        scrape_result = scrape_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following info about '{topic}', "
                        f"scrape the relevant urls for detailed info: {state['search_result'][:4000]}",
                    )
                ]
            }
        )
        state["scrape_result"] = _last_text(scrape_result)

    print("\nscrape result", state["scrape_result"])

    # writer chain
    print("\n" + "=" * 20)
    research_combine = (
        f"SEARCH RESULT:\n{state['search_result']}\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scrape_result']}"
    )

    state["report"] = writer_chain.invoke(
        {
            "topic": topic,
            "research": research_combine,
        }
    )

    print("\nfinal report\n", state["report"])

    # critic report
    print("\n" + "=" * 20)
    state["feedback"] = critic_chain.invoke({"report": state["report"]})

    print("\ncritic report\n", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("enter the topic: ").strip()
    run_research_pipeline(topic)
