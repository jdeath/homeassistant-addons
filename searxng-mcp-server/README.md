# Home assistant add-on: Searxng-mcp-server

A lightweight MCP server that gives llama.cpp (and any other MCP-compatible client) web search via a private [SearXNG](https://github.com/searxng/searxng) instance. 

MCP server adapted from https://github.com/jdeath/mcp-searxng-enhanced to give an FastMCP IP endpoint (used AI to edit). Standalone MCP code at https://github.com/jdeath/mcp-searxng-enhanced

Use this if you have an existing SearXNG installation. Use my other addon if you do not already have an installation, because it includes the MCP server inside the SearXNG container `https://github.com/jdeath/homeassistant-addons/tree/main/searxng_with_mcp`. 

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation


1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Setup SearXNG. I used home assistant addon: https://github.com/DDanii/HA-Add-ons-by-DDanii
1. Be sure to allow json format in the SEARXNG settings of the SearXNG server config.yaml
1. Set the options under configuration tab. Point to URL of your SearXNG instance. be sure ends in `/search`
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. You should not need edit the MCP server settings in addon_configs/2effc9b9_searxng_mcp_server/ods_config.json file, but you can. The server/ports/host should not be touched.
1. Point llama.cpp MCP server to http://IP:PORT/mcp 
1. Point claude command line to: MCP server to http://IP:PORT/mcp with `claude mcp add --transport http searxng http://IP:PORT/mcp`
1. In claude code search with: search for XXX
1. In llama.cpp, search should just work like normal


[repository]: https://github.com/jdeath/homeassistant-addons
