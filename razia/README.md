# Home assistant add-on: Razzia

Razzia is a straightforward and open-source quiz platform, allowing users to host it on their own server for smaller events.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/Ralex91/Razzia).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Open WebUI via <your-ip>:port.
1. You should get a login error
1. review log to find client IP address to add to whitelist section
1. Go to /addon_configs/2effc9b9_razzia
1. edit /addon_configs/2effc9b9_razzia/game.json add password
1. restart addon
1. Access the manager interface at http://localhost:3000/manager
1. Enter the manager password (game.json)
1. Share the game URL (http://localhost:3000) and room code with participants
1. Wait for players to join
1. Click the start button to begin the game


## Configuration

```
port : 8000 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
