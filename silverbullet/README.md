# Home assistant add-on: MeTube

SilverBullet is a note-taking application optimized for people with a hacker mindset. We all take notes. There’s a million note taking applications out there. Literally. Wouldn’t it be nice to have one where your notes are more than plain text files? Where your notes essentially become a database that you can query; that you can build custom knowledge applications on top of? A hackable notebook, if you will?


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/silverbulletmd/silverbullet).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.
1. Data should live in /addon_config/2effc9b9_silverbullet
## Configuration

```
port : 8081 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
