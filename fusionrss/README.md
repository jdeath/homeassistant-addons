# Home assistant add-on: Fusion RSS

A lightweight RSS feed aggregator and reader.

Key features include:

- Group, Bookmark, Search, Sniff feeds automatically
- Import/Export OPML file
- Support RSS, Atom, JSON types feed
- Responsive, Light/Dark mode, PWA
- Lightweight, Self-hosted friendly
  - Built with Golang and SQLite, Deploy with a single binary
  - Pre-built Docker image
  - Uses about 80MB of memory
  
_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/0x2E/fusion).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.
1. Your data is stored in /addon_configs/2effc9b9_fusionrss

## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
