# Home assistant add-on: Vaultwarden

Alternative implementation of the Bitwarden server API written in Rust and compatible with upstream Bitwarden clients*, perfect for self-hosted deployment where running the official resource-heavy service might not be ideal.

Difference between this version, the official homeassistant addon and Alex Belgium's addon is this stores the data in /addons_config which makes it easier to move things around if you accidentally uninstall or have a bad upgrade. You must be sure to use an argon encrypted password, which should be default now. Also the built-in homeassistant one often is not updated (even after multiple requests). This addon also just runs the raw docker container, where the other addons edit the container.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/dani-garcia/vaultwarden).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port.
1. Your data will be stored in /addon-configs/2effc9b9_vaultwarden/

If you have an existing vaultwarden installation (default addon or alexbelgium's),
1. Ensure my addon has been run once, but then make sure to stop it
1. log into homeassistant cli
1. `docker ps | grep "vault"`
1. find the docker containerID
1. `docker cp CONTAINERID:/data /addon-configs/2effc9b9_vaultwarden/`
1. then in `/addon-configs/2effc9b9_vaultwarden/` move everything out of `data` folder into `/addon-configs/2effc9b9_vaultwarden/`
1. all the files should now be in `/addon-configs/2effc9b9_vaultwarden/`
1. stop default addon, turn off "start on boot"
1. start my addon


## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
