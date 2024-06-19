# Home assistant add-on: MS Rewards Farmer

## Description
Automatically get points for the MS Rewards program and does all the tasks for you (playing quizzes, searches...)

This is a dockerized version of [**@klept0**](https://github.com/klept0)'s fork of the MS-Rewards-Farmer (initially coded by [**@charlesbel**](https://github.com/charlesbel)). It runs completely headless in a docker environment with google chrome and xvfb as virtual display

Based on LtCMDstone Docker Image: https://github.com/LtCMDstone/MS-Rewards-Farmer-Docker, but this add-on builds the docker file locally on your home assistant machine. The Dockerfile/Entrypoint.sh is basically copied from LtCMDstone. This way chrome and the farmer code will get updated if you rebuild the addon and be less likely to get out of sync.

Currently using a Fork of @klept0 repo, as it needs a patch to run in docker. 

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on. It will fail, this is ok
1. go to `/addon-configs/2effc9b9_msrewardsfarmer`
1. Edit the accounts.json with your username and password. Delete the second entry if there is one.
1. (Optional) Edit `/addon-configs/2effc9b9_msrewardsfarmer/config.yaml` to send a notification (see below)
1. Run the addon again and check the logs
1. After confirmed working, use an automation to run this once a day

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
  urls:
    - 'hassio://192.168.X.XX/eyXXXXXXXXXXXXXXXX.eyXXXXXXXXXXXXXXXXXxx'
```
Where the `eyXXX.eyXXX` string is a Home Assistant Long-Lived Token. Long-lived access tokens can be created using the "Long-Lived Access Tokens" section at the bottom of a user's Home Assistant profile page.

More details here: `https://github.com/caronc/apprise/wiki/Notify_homeassistant`

# Issues
The farmer code will be copied to `/addon-configs/2effc9b9_msrewardsfarmer` . This is needed to load the config and keep the logs accessable. When rebuilding the app it *should* update this code. However, if have issues, first delete `main.py` and the `src/` directory.

Still a work in progress and sometimes the farmer will crash, as headless chrome can be buggy.

[repository]: https://github.com/jdeath/homeassistant-addons
