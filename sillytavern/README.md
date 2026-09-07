# Home assistant add-on: SillyTavern

SillyTavern provides a single unified interface for many LLM APIs (KoboldAI/CPP, Horde, NovelAI, Ooba, Tabby, OpenAI, OpenRouter, Claude, Mistral and more), a mobile-friendly layout, Visual Novel Mode, Automatic1111 & ComfyUI API image generation integration, TTS, WorldInfo (lorebooks), customizable UI, auto-translate, more prompt options than you'd ever want or need, and endless growth potential via third-party extensions.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/SillyTavern/SillyTavern/).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Open WebUI via <your-ip>:port.
1. You should get a login error
1. review log to find client IP address to add to whitelist section
1. Go to /addon_configs/2effc9b9_sillytavern
1. edit /addon_configs/2effc9b9_sillytavern/config.yaml and add client ip address into `whitelist:` section
1. restart addon
1. Open WebUI via <your-ip>:port
1. Should work. If not, play with config.yaml
1. Edit options from within addon, connect to llm, etc
## Configuration

```
port : 8000 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
