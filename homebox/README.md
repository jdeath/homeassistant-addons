# Home assistant add-on: Homebox

Homebox is the inventory and organization system built for the Home User! With a focus on simplicity and ease of use, Homebox is the perfect solution for your home inventory, organization, and management needs. While developing this project, I've tried to keep the following principles in mind:

- _Simple_ - Homebox is designed to be simple and easy to use. No complicated setup or configuration required. Use either a single docker container, or deploy yourself by compiling the binary for your platform of choice.
- _Blazingly Fast_ - Homebox is written in Go, which makes it extremely fast and requires minimal resources to deploy. In general, idle memory usage is less than 50MB for the whole container.
- _Portable_ - Homebox is designed to be portable and run on anywhere. We use SQLite and an embedded Web UI to make it easy to deploy, use, and backup.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/sysadminsmedia/homebox).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.
1. Register a user
1. Go to add-on configuration and disable user registration, if you desire
## Configuration

```
port : 7745 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
