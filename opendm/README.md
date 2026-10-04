# Home assistant add-on: Open Dungeon Master

## Description
Open Dungeon Master runs multiplayer (and solo) Dungeons & Dragons 5e campaigns with an AI Dungeon Master, on your own machine. The narrator is whichever AI you already have: a local model (llama.cpp, Ollama, LM Studio, vLLM), an API key (OpenAI, OpenRouter, or any OpenAI-compatible endpoint), or a CLI agent you already pay for (Claude Code, Codex, opencode, Grok Build), which narrates on its own subscription with no API key handed over. The model is the creative mind and narrator; a stack of server-side engines enforces the 5e rules for both the players and the DM. The narrator never owns the numbers: dice, hit points, spell slots, conditions, and the death track are computed and clamped by the backend, and the model changes game state only through tools the server validates.

From: https://github.com/Lebbitheplow/open-dungeon-master

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on. It will fail, this is ok
1. go to /addon-configs/2effc9b9_opendm
1. Create and Edit `/addon-configs/2effc9b9_opendm/env.server`
	add this line:
	`DB_ENCRYPTION_KEY=58979662b0146318a9c4d8bd3bda1b65e7ccfeae5896f9ddaebeec17ebd32ddf`

	This is a dummy value, replace with running: `openssl rand -hex 32`

1. Run the addon again and check the logs
1. Login in at IP:3005, create first user (will be the addin)
1. You must manually install the content pack
1. log into your home assistant via SSH
1. `docker ps`
1. find the running container and log into it
1. `docker exec -it CONTAINERCODE /bin/bash`
1. `node scripts/import-open5e.mjs` then `exit`
1. Restart addon
1. Then setup AI and begin playing


[repository]: https://github.com/jdeath/homeassistant-addons


