# Home assistant add-on: Minecraft Dedicated Server Bedrock Edition
A quick way to run a Minecraft Dedicated Server Bedrock Edition on Home Assistant.
 
_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [itzg/docker-minecraft-bedrock-server](https://github.com/itzg/docker-minecraft-bedrock-server/) docker image.

When restarting the addon, it will automatically fetch the latest version of minecraft.

Your world,,settings, and the server executable are stored in /share/minecraftbe

You may want to create a service to restart the addon in the middle of the night so it updates the minecraft version (see below)

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
2. Change the API port if desired (defaults to standard minecraft port)
3. Click the `Save` button to store your configuration.
4. Make the directory /share/minecraftbe
5. Start the add-on.
6. Check the logs of the add-on to see if everything went well.
7. Edit any server/permissions/whitelist properties you want in /share/minecraftbe/ and restart addon
8. If you want external access, be sure to forward your external port to your homeassistant IP.

## Restart Automation

```
alias: Restart Minecraft Server
description: ""
trigger:
  - platform: time
    at: "02:00:00"
condition:
  - condition: time
    before: "00:00:00"
    weekday:
      - mon
      - wed
      - fri
    after: "00:00:00"
action:
  - service: hassio.addon_restart
    data:
      addon: 2effc9b9-minecraftbe
mode: single
```
[repository]: https://github.com/jdeath/homeassistant-addons
