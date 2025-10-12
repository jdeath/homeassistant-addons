# Home assistant add-on: CommaFeed

Google Reader inspired self-hosted RSS reader, based on Quarkus and React/TypeScript.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/Athou/commafeed/).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port and ingress. Default user:password is admin:admin
1. Settings will be in /addon_configs/2effc9b9_commafeed

## Configuration
You can set the addon to use a environment file if you choose. Note use '/commafeed/data' as base path which will map to /addon_configs/2effc9b9_commafeed 

The config file in the UI will `/commafeed/data/config.env` , but you make the file `addon_configs/2effc9b9_commafeed/config.env` 
You need to create the file yourself and make it a list of environments you want to set, like:
```
COMMAFEED_USERS_ALLOW_REGISTRATIONS=true
```
```
port : 8082 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
