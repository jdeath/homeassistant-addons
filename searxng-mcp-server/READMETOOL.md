# SearXNG MCP Server

A lightweight MCP server that gives Ollama (and any other MCP-compatible client) web search via a private [SearXNG](https://github.com/searxng/searxng) instance. Uses the **streamable-HTTP** transport over a single `/mcp` endpoint.

---

## Requirements

- Python 3.9+
- A running SearXNG instance (local or Docker)
- Ollama with a model that supports tool calling (e.g. `llama3.1`, `qwen2.5`, `mistral-nemo`)

---

## SearXNG Setup

If you don't have a SearXNG instance yet, spin one up with Docker:

```bash
docker run -d \
  --name searxng \
  --restart always \
  -p 8080:8080 \
  -v searxng-data:/etc/searxng \
  -e BASE_URL=http://localhost:8080/ \
  -e INSTANCE_NAME=local \
  searxng/searxng
```

Enable the JSON format in SearXNG's `settings.yml` (required for this server):

```yaml
search:
  formats:
    - html
    - json
```

---

## Installation

```bash
git clone <your-repo-url>
cd go_mcp_server_searxng-main
pip install -r requirements.txt
```

---

## Configuration

Copy `.env` and edit the values:

```bash
cp .env .env.local  # or edit .env directly
```

| Variable           | Default                    | Description                        |
|--------------------|----------------------------|------------------------------------|
| `SEARXNG_BASE_URL` | `http://localhost:8090`    | Base URL of your SearXNG instance  |
| `HOST`             | `0.0.0.0`                  | Interface to bind to               |
| `PORT`             | `32769`                    | Port to listen on                  |

---

## Running

```bash
python server.py
```

The server starts on `http://0.0.0.0:32769/mcp`.

---

## Connecting to Ollama

Ollama's MCP support is configured in `~/.ollama/config.json` (or wherever your client stores MCP config). Add:

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://localhost:32769/mcp"
    }
  }
}
```

If Ollama is running in Docker and the MCP server is on the host:

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://host.docker.internal:32769/mcp"
    }
  }
}
```

---

## Connecting to Other Clients

**Open WebUI / any streamable-HTTP client:**

```
http://<server-ip>:32769/mcp
```

**Claude Desktop / Cursor / Windsurf:**

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://localhost:32769/mcp"
    }
  }
}
```

---

## Search Tool

The server exposes one tool: **`search`**

| Parameter    | Type   | Default     | Description                                                              |
|--------------|--------|-------------|--------------------------------------------------------------------------|
| `query`      | string | *(required)*| The search query                                                         |
| `category`   | string | `general`   | `general`, `news`, `images`, `videos`, `science`, `files`, `social media`|
| `time_range` | string | *(all time)*| `day`, `week`, `month`, `year`                                           |
| `language`   | string | `en`        | BCP 47 language code, e.g. `en`, `fr`, `de`                             |

Returns the top 10 results as a numbered plain-text list (title, URL, snippet) — formatted for LLM consumption rather than raw JSON.

---

## License

MIT
