# Home assistant add-on: FreeBeeGee

# FreeBeeGee

A virtual gaming tabletop you can host on your own server.

Your game. Your data.

## Key features

* Browser-based 2D virtual tabletop for board- and role-playing games.
* Easy-to-use drag'n'drop interface. Keyboard hotkeys for power-users.
* Invite friends by sending them a room's unique URL. Room passwords optional.
* Multiple tables per room. Use them for different game setups or dungeon levels.
* Tile-/grid-based. Supports square and hex layouts, with snapping.
* Classic game boards, dungeon tiles and 200+ monster token included. Upload your own, too.
* Separate layers for tiles, sticker and token.
* Asset browser for your token/tiles. Individual libraries per room/game.
* Sticky notes and dice trays.
* Templates to setup tables and populate your library from.
* Download snapshots/savegames of your rooms, transfer them between servers or keep an offline backup.
* Privacy friendly. No user tracking. No 3rd-party scripts. Rooms are deleted after some (configurable) time, usually 48h.
* File & folder-based. No database required. Easy to install.
* Open source software (AGPL-3.0). Server/API written in PHP, client in JavaScript..

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/ludus-leonis/FreeBeeGee).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port.
1. Settings will be in `/addon_configs/2effc9b9_freebeegee`
1. The web interface should prompt you to make a admin password. Create password and paste it into `/addon_configs/2effc9b9_freebeegee/server.json` in the correct field
## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
