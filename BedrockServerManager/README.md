# Home assistant add-on: BedrockServerManager

Bedrock Server Manager is a comprehensive python server designed for installing, managing, and maintaining Minecraft Bedrock Dedicated Servers with ease

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/DMedina559/bedrock-server-manager).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Go to the local IP of home assistant with the port you configured (defaults to 11325)
1. Settings will be in /addon_configs/2effc9b9_bedrockservermanager
1. This folder will be /root/ in the documentation for bedrock-server-manager


```
port : 11325 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
