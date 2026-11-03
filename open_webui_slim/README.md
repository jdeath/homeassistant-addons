# Home assistant add-on: NutriTrace

## Description
Open WebUI is **a home for AI**, a self-hosted AI platform that's **[extensible](https://docs.openwebui.com/features/extensibility/plugin/)**, **[feature-rich](https://docs.openwebui.com/features/)**, user-friendly, and built to run **[entirely offline](https://openwebui.com/sovereign-ai)**. With support for **Ollama** and **OpenAI-compatible APIs**, it gives you a powerful, provider-agnostic interface for both local and cloud-based models.


If you want the version which includes local AI in the image, use `https://github.com/mikastamm/open-webui-homeassistant-addon`

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Highly recommend change the default WEBUI_SECRET_KEY to output of `openssl rand -hex 32` (ssh into home assistant and run)
1. Click the `Save` button to store your configuration.
1. Ingress will work AFTER you setup the server

[repository]: https://github.com/jdeath/homeassistant-addons


