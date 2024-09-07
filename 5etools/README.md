# Home assistant add-on: 5etools

A suite of browser-based tools for players and DMs of D&D 5e. Downloads posted image from 5etools GitHub. No image or content is hosted/posted on jdeath's repo. No support given as Home Assistant Addon creator does not use this. Self-hosted image can be a revision behind the 5etools website. Image is 4 GB, so will take a long time to install, be patient.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/5etools-mirror-2/5etools-mirror-2.github.io).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on. 4 GB image will take a while to download
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.

## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
