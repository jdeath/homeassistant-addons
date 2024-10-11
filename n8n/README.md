# Home assistant add-on: n8n

n8n is an extendable workflow automation tool. With a fair-code distribution model, n8n will always have visible source code, be available to self-host, and allow you to add your own custom functions, logic and apps. n8n's node-based approach makes it highly versatile, enabling you to connect anything to everything.

Functionality not tested, but addon does run

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/n8n-io/n8n).

## Installation


1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Add-on will fail, that is ok
1. ssh into your homeassistant and run `chmod 2777 /addon_configs/2effc9b9_n8n`
1. start add-on
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port.
1. Setup administrator account
1. Settings will be in /addon_configs/2effc9b9_n8n
## Configuration

```
port : 5678 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
