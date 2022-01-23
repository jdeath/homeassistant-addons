# Home assistant add-on: EmulatorJS
 In browser web based emulation portable to nearly any device for many retro consoles. A mix of emulators is used between Libretro and EmulatorJS.
 
 
_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/linuxserver/docker-emulatorjs) from linuxserver. In browser web based emulation portable to nearly any device for many retro consoles. A mix of emulators is used between Libretro and EmulatorJS.

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Make the directory /share/emulatorjs to store your games/art files
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Place roms in the correct folders in /share/emulatorjs/
1. Open WebUI should ingress the PlayerUI, go to your local homeassistant IP:port or the admin port.
1. Go to the admin port manually to setup games
1. Consult official docs for setup support: https://github.com/linuxserver/docker-emulatorjs
1. If starting addon results in wiping your setup, stop addon, and restart. Sometimes the mapping to /share/emulatorjs does not work
2. 
## Configuration

```
adminport : 3000 #port you want to run admin interface on.
port: 89 # port you want to run frontend on
```

Webui can be found at `<your-ip>:port`. Should be available via ingress. The adminport is not available via ingress

[repository]: https://github.com/jdeath/homeassistant-addons
