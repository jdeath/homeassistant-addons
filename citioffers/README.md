# Home assistant add-on: Citi Merchant Offers

## Description
Loads your account and activates all citibank merchant offers. Use an automation to run automatically every couple days. Totally vibe coded! Not fully tested and use at your own risk.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on. It will fail, this is ok
1. go to /addon-configs/2effc9b9_citioffers
1. Edit `/addon-configs/2effc9b9_citioffers/credentials.yaml` (see below)
1. Run the addon again and check the logs
1. After confirmed working, use an automation to run this once a day

## credentials.yaml
```
user: CITIBANK_USERNAME
password: CITIBANK_PASSWORD
```

## Automatic Running
1. Create an automation to run this addon once a day (at a random time)

```
alias: Start Citi Offers
description: ""
trigger:
  - platform: time
    at: "06:00:00"
condition: []
action:
  - delay: "{{ (range(0, 1)|random|int) }}:{{ (range(1, 59)|random|int) }}:00"
  - service: hassio.addon_start
    data:
      addon: 2effc9b9_citioffers
mode: single
```


[repository]: https://github.com/jdeath/homeassistant-addons


