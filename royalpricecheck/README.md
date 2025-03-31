# Home assistant add-on: Royal Price Check

## Description
Notify if Royal Caribbean Cruise addons get cheaper. Can reprice the cruise, just drink package, internet, excursions, etc

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on. It will fail, this is ok
1. go to /addon-configs/2effc9b9_royalpricecheck
1. Edit `/addon-configs/2effc9b9_royalpricecheck/config.yaml` (see below)
1. Run the addon again and check the logs
1. After confirmed working, use an automation to run this once a day

## Config.yaml
See `https://github.com/jdeath/CheckRoyalCaribbeanPrice`

## Automatic Running
1. Create an automation to run this addon once a day (at a random time)

```
alias: Start Royal Price Check
description: ""
trigger:
  - platform: time
    at: "06:00:00"
condition: []
action:
  - delay: "{{ (range(0, 1)|random|int) }}:{{ (range(1, 59)|random|int) }}:00"
  - service: hassio.addon_start
    data:
      addon: 2effc9b9_royalpricecheck
mode: single
```

# Sending a notification.
1. edit `/addon-configs/2effc9b9_royalpricecheck/config.yaml`
1. Configure the line for a notification

It should look something like this for homeassistant notification:
```
# config.yaml
apprise:
  urls:
    - 'hassio://192.168.X.XX/eyXXXXXXXXXXXXXXXX.eyXXXXXXXXXXXXXXXXXxx'
```
Where the `eyXXX.eyXXX` string is a Home Assistant Long-Lived Token. Long-lived access tokens can be created using the "Long-Lived Access Tokens" section at the bottom of a user's Home Assistant profile page.

More details here: `https://github.com/caronc/apprise/wiki/Notify_homeassistant`

More details here: `https://github.com/caronc/apprise` You can include multiple URL lines to send emails, etc
# Add To Sidebar
Since there is no WebUI, this cannot be shown in the sidebar. However you can add the following code to your Home Assistant `configuration.yaml` to show the log via a sidebar entry

```
panel_custom:
  - name: panel_rewards
    sidebar_title: Rewards
    sidebar_icon: mdi:medal
    url_path: 'hassio/addon/2effc9b9_royalpricecheck/logs'
    module_url: /api/hassio/app/entrypoint.js
    embed_iframe: true
    require_admin: true
```

# Issues


[repository]: https://github.com/jdeath/homeassistant-addons


