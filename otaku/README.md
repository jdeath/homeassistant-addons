# Home assistant add-on: Otaku

Otaku is free and open source, runs on your own computer, needs no infrastructure, installs in one
command, and requires minimal configuration. LLMs can be local (via llama.cpp, KoboldCpp, Ollama,
and others) or accessed via an API service (OpenRouter, NanoGPT).

The three pillars of otaku:

- **maintain writing quality** as the story grows;
- **keep the context small**, even for long stories, without losing the details that matter;
- **high-quality interfaces**, in the browser and in the terminal.


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

Using binaries from fork: https://github.com/enclavum/otaku

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port.

## Configuration

```
port : 8081 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.


[repository]: https://github.com/jdeath/homeassistant-addons
