# Home assistant add-on: PlanarAlly

# PlanarAlly

A companion tool for when you travel into the planes.

PlanarAlly is a web tool that adds virtual battlemaps with various extras to your TTRPG/D&D toolbox.

Some key features are:

**Self hosting**: You can run this software wherever you like without having to rely on an external service\
**Offline support**: This tool can be used in a completely offline set-up for when you play D&D in a dark dungeon.

**Simple layers**: Organize your scenes in layers for easier management.\
**Infinite canvas**: When a limited workspace is still not enough!\
**Dynamic lighting**: Increase your immersion by working with light and shadows.\
**Player vision**: Limit vision to what your token(s) can see. Is your companion in a different room, no light for you!\
**Initiative tracker**: Simple initiative tracker\
**Floors!**: Look down upon lower floors when standing on a balcony!

This tool is provided free to use and is open source.


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/Kruptein/PlanarAlly).

## Installation

The installation of this add-on takes a few extra steps.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. It will fail, that is ok
1. Settings will be in `/addon_configs/2effc9b9_plannarally`
1. ssh in to homeassistant type `chmod 2777 addon_configs/2effc9b9_plannarally`
2. Start the add-on, it will start, but then stop the addon.
1. edit `/addon_configs/2effc9b9_plannarally/server_config.cfg`
1. Under `[General]` make the next two lines:

```
save_file = /config/planar.sqlite
assets_directory = /config/assets
```
1. Restart the addon
1. Open WebUI, should work via <your-ip>:port.
## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
