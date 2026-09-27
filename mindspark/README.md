# Home assistant add-on: Mind Spark

MindSpark is an open-source mind-mapping app you actually own - no accounts, no paywalls, no feature gates, no usage limits. Self-host it in one command, run it free in the browser with every map saved to your own private GitHub repo, or add one small Cloudflare Worker to unlock real-time sharing and collaboration. It's vanilla JavaScript with zero runtime dependencies, MIT-licensed, AI-assisted, and yours to run, modify, and extend

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/prasadpatil25/MindSpark).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Addon will fail
1. ssh into home assistant: `chmod 2777 /addon_configs/local_mindspark/`
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.

## Configuration

```
port : 3000 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
