# Home assistant add-on: Rewards Farmer

## Description
Automation for MS Rewards based on https://youtu.be/4qdPcMNaioA.

Upstream does not use releases. So you need to monitor for changes and rebuild.

IMPORTANT: Use at your own risk. Microsoft may take action against your account for using automated scripts to gain rewards points. The YouTube video contains more details about the techniques implemented to avoid detection of this script.

Based on https://github.com/User0332/rewards-farmer/

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Set mode to signin. Click the `Save` button to store your configuration.
1. Start the add-on. 
1. Go to http://homeassistantIP:6080 and log into bing rewards. close the edge window
1. Set mode to run. Click the `Save` button to store your configuration.
1. Restart addon
1. After confirmed working, use an automation to run this once a day

## Upgrading
1. Upstream does not use releases, so you must monitor `https://github.com/User0332/rewards-farmer/` for updates
1. Uninstall addon
1. ssh into home assistant and run `docker builder prune`
1. Reinstall addon
1. Since this addon builds the docker image from upstream github source, simply rebuilding the addon may not pull down latest source.
1. If no longer works, please create an issue. A required change in the upstream DOCKERFILE will require changes to the addon

## Automatic Running
1. Create an automation to run this addon once a day (at a random time)

```
alias: Start MS Rewards Farmer
description: ""
trigger:
  - platform: time
    at: "06:00:00"
condition: []
action:
  - delay: "{{ (range(0, 1)|random|int) }}:{{ (range(1, 59)|random|int) }}:00"
  - service: hassio.addon_start
    data:
      addon: 2effc9b9_rewardsfarmernew
mode: single
```

[repository]: https://github.com/jdeath/homeassistant-addons


