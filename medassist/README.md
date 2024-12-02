# Home assistant add-on: MedAssist

MedAssist is a simple Node.js application made with love to help my partner manage their daily medications. It makes it easy to keep track of medication inventory and reorder on time by sending reminders. If you're unsure whether a dose was taken, just check the dashboard, and comparing the expected stock with the actual quantity can help confirm. For travel, MedAssist takes away the stress by generating a quick list of all necessary medications for the time you’ll be away.

## Features
If you take at least one medication on a regular schedule, this app might be useful. But if you manage multiple medications with complex schedules, you might enjoy it even more.

- Track medication inventory and know exactly when to reorder
- Receive email reminders when supplies are low
- Generate a custom medication list for travel, including quantities needed for your chosen timeframe (optionally send by e-mail)
- Simple dashboard showing medication status and upcoming schedules
- User friendly web interface for easy medication management and configuration


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/njic/medassist/releases).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port
1. Settings will be in /addon_configs/2effc9b9_medassist
## Configuration

```
port : 3111 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
