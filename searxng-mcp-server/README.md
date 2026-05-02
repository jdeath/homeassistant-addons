# Home assistant add-on: Searxng-mcp-server

A lightweight MCP server that gives llama.cpp (and any other MCP-compatible client) web search via a private [SearXNG](https://github.com/searxng/searxng) instance. Uses the **streamable-HTTP** transport over a single `/mcp` endpoint.

Adapted from https://github.com/The-AI-Workshops/searxng-mcp-server using Claude


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation


1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Setup SearXNG. I used home assistant addon: https://github.com/DDanii/HA-Add-ons-by-DDanii
1. Be sure to allow json in the SEARXNG settings in the SearXNG config.yaml
1. Set the options under configuration tab. Point to URL of your SearXNG instance
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Point llama.cpp MCP server to http://IP:PORT/mcp 
1. Point claude command line to: MCP server to http://IP:PORT/mcp with `claude mcp add --transport http searxng http://IP:PORT/mcp`
1. In claude code search with: searxng search for XXX
1. In llama.cpp, search should just work like normal


[repository]: https://github.com/jdeath/homeassistant-addons
