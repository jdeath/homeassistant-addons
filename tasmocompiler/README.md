# Home assistant add-on: tasmocompiler
 TasmoCompiler is a simple web GUI which allows you to compile fantastic Tasmota firmware with your own settings
 
_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://hub.docker.com/r/benzino77/tasmocompiler) 

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Go to the local IP:port . Ingress does not work for some reason
1. Consult official docs for setup support: https://github.com/benzino77/tasmocompiler
## Configuration

```
port: 3000 # port you want to run frontend on
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
