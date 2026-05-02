from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from dataclasses import dataclass
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import os

load_dotenv()

@dataclass
class AppContext:
    client: httpx.AsyncClient

@asynccontextmanager
async def lifespan(server: FastMCP):
    async with httpx.AsyncClient(
        base_url="http://localhost:8080", # Fixed as inside docker
        timeout=30,
    ) as client:
        yield AppContext(client=client)

mcp = FastMCP(
    "searxng",
    lifespan=lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8081")),
    stateless_http=True,
)

@mcp.tool()
async def search(
    ctx: Context,
    query: str,
    category: str = "general",
    time_range: str = "",
    language: str = "en",
) -> str:
    """
    Search the web using SearXNG. Use this to find current information, news, facts, or any topic.

    Args:
        query: The search query string.
        category: One of: general, news, images, videos, science, files, social media.
        time_range: Restrict results by age — one of: day, week, month, year. Leave empty for all time.
        language: BCP 47 language code for results, e.g. 'en', 'fr', 'de'. Defaults to 'en'.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context

    params: dict = {
        "q": query,
        "format": "json",
        "categories": category,
        "language": language,
    }
    if time_range:
        params["time_range"] = time_range

    try:
        resp = await app_ctx.client.get("/search", params=params)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"Search failed: {e}"

    results = data.get("results", [])
    if not results:
        return f'No results found for "{query}".'

    lines = [f'Search results for "{query}":\n']
    for i, r in enumerate(results[:10], 1):
        title   = r.get("title", "").strip()
        url     = r.get("url", "")
        snippet = (r.get("content") or r.get("description") or "").strip()
        lines.append(f"{i}. {title}")
        lines.append(f"   {url}")
        if snippet:
            lines.append(f"   {snippet[:400]}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    app = mcp.streamable_http_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8081")),
    )
