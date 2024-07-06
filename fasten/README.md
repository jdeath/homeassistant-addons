# Home assistant add-on: Fasten

## Description
Fasten securely connects your healthcare providers together, creating a personal health record that never leaves your hands

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

This addon takes a few extra steps.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on. It will fail, this is ok
1. go to /addon-configs/2effc9b9_fasten
1. Download the base configuration file from `https://raw.githubusercontent.com/fastenhealth/fasten-onprem/main/config.yaml`
1. Copy this file into `/addon-configs/2effc9b9_fasten`
1. edit `/addon-configs/2effc9b9_fasten\config.yaml` and change the `database->location` entry to `/config/fasten.db`
1. You should change the jwt token too

[repository]: https://github.com/jdeath/homeassistant-addons
