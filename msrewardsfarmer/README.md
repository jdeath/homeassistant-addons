# Home assistant add-on: MS Rewards Farmer

## Description
Automatically get points for the MS Rewards program and does all the tasks for you (playing quizzes, searches...)

This is a dockerized version of [**@klept0**](https://github.com/klept0)'s fork of the MS-Rewards-Farmer (initially coded by [**@charlesbel**](https://github.com/charlesbel)). It runs completely headless in a docker environment with google chrome and xvfb as virtual display

Docker implantation leveraged the work of LtCMDstone Docker Image: https://github.com/LtCMDstone/MS-Rewards-Farmer-Docker

This homeassistant version will update Chrome when installing/rebuilding addon. This will keep chrome up to date. I am probably doing something wrong, but the addon seems to work. If you have a cleaner way to build the addon, please do a PR.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Set your GEO and LANG if not `US` (United States) and `en` (english)
1. Start the add-on. It will fail, this is ok
1. go to /addon-configs/2effc9b9_msrewardsfarmer
1. Copy the baseline config file from: `https://github.com/klept0/MS-Rewards-Farmer`
1. Edit `/addon-configs/2effc9b9_msrewardsfarmer/config.yaml`
1. Run the addon again and check the logs
1. After confirmed working, use an automation to run this once a day

## GEO and Lang
This must be set correctly, because MS might only allows you to get points from one county a day, effectively disabling this farmer or your standard way of getting points.

1. Go to https://trends.google.com/trends/
1. Change your country. The URL should end with =XX wheere XX is the GEO code to use. Must be capitalized
1. Language defaults to English (en). Use the proper code to change the language if desired

## Automatic Running
1. Create an automation to run this addon once a day (at a random time to avoid ban)

```
alias: Start MS Rewards Farmer
description: ""
trigger:
  - platform: time
    at: "05:00:00"
condition: []
action:
  - delay: "{{ (range(0, 1)|random|int) }}:{{ (range(1, 59)|random|int) }}:00"
  - service: hassio.addon_start
    data:
      addon: 2effc9b9_msrewardsfarmer
mode: single
```

# Sending a notification.
1. edit `/addon-configs/2effc9b9_msrewardsfarmer/config.yaml`
1. Configure the line for a notification

It should look something like this for homeassistant notification:
```
# config.yaml
apprise:
  summary: ALWAYS
  urls:
    - 'hassio://192.168.X.XX/eyXXXXXXXXXXXXXXXX.eyXXXXXXXXXXXXXXXXXxx'  # Replace with your actual Apprise service URLs
attempts:
retries:
  base_delay_in_seconds: 14 # base_delay_in_seconds * 2^max = 14.0625 * 2^6 = 900 = 15 minutes
  max: 7
  strategy: EXPONENTIAL
```
Where the `eyXXX.eyXXX` string is a Home Assistant Long-Lived Token. Long-lived access tokens can be created using the "Long-Lived Access Tokens" section at the bottom of a user's Home Assistant profile page.

More details here: `https://github.com/caronc/apprise/wiki/Notify_homeassistant`

# Add To Sidebar
Since there is no WebUI, this cannot be shown in the sidebar. However you can add the following code to your Home Assistant `configuration.yaml` to show the log via a sidebar entry

```
panel_custom:
  - name: panel_rewards
    sidebar_title: Rewards
    sidebar_icon: mdi:medal
    url_path: 'hassio/addon/2effc9b9_msrewardsfarmer/logs'
    module_url: /api/hassio/app/entrypoint.js
    embed_iframe: true
    require_admin: true
```

# Issues

If you are having issues first ask - did I make sure I have updated all of the files and cleared the sessions folder before running again?

Still a work in progress and sometimes the farmer will crash or run slowly, as headless chrome can be buggy. Just run it again when crashes. Having a notification sent to home assistant makes this easy to see.

[repository]: https://github.com/jdeath/homeassistant-addons
