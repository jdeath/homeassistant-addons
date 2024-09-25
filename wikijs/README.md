# Home assistant add-on: Wiki.js

A modern, lightweight and powerful wiki app built on NodeJS

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/requarks/wiki).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on. Add-on will error
1. Copy default configuration [wikijs-config.yml](https://github.com/jdeath/homeassistant-addons/blob/main/wikijs/wikijs-config.yml) (not config.yaml!) from this repo to /addon_configs/2effc9b9_wikijs
1. start addon
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port.
1. Settings and sqlite database will be in /addon_configs/2effc9b9_wikijs (mounted in addon as /config)
1. Stop addon, edit settings.yaml file to change anything you need, such as changing to another database
## Configuration

```
port : 3000 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
