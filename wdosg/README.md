# Home assistant add-on: wDOSg

wDOSg (web DOS games) is a centralized DOS game library that allows you to fetch metadata from IGDB and run your games on the browser through js-dos, using a minimalistic configuration..

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/SoulRaven80/wdosg).

## Installation

The installation of this add-on takes a bit of extra work.
1. Consult the official [repo](https://github.com/SoulRaven80/wdosg)
1. Get a Twitch Developer Account [instructions](https://api-docs.igdb.com/#account-creation).
1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. This addon takes the CLIENT_ID and the SECRET. It will get the token for you.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port
1. Default user/password = wdosg@wdosg.com / wdosg
1. Consult official documentation to make a jsdos bundle. It is kind of a pain! Latest version can do it directly from your own zip of a game. Be sure the zipfile has the game directly in the root of the zip, not in a folder inside the zip!
1. Upload your bundle and play your game.
1. Settings will be in /addon_configs/2effc9b9_wdosg
## Configuration

```
port : 3001 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
