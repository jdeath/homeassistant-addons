# Home assistant add-on: Free Games Claimer Remaster

Not a fork – a complete ground-up Python remaster inspired by vogler/free-games-claimer.

This version uses the stock Free Games Claimer Remaster docker imager, versus rebuilding it (as alexbelgium does). This addon will track beta versions too.

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/P-Adamiec/Free-Games-Claimer-Remaster).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. It will fail
1. Download the stock configuration [.env](https://raw.githubusercontent.com/P-Adamiec/Free-Games-Claimer-Remaster/refs/heads/main/.env.example) and copy it to `/addon_configs/2effc9b9_freegamesremaster/config.env`
1. Edit as needed with passwords. Set VNCIP to your home assistant internal IP
1. Restart addon
1. Got to IP:port to watch login and manually log in as needed.


[repository]: https://github.com/jdeath/homeassistant-addons
