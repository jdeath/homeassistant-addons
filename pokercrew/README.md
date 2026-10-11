# Home assistant add-on: Poker Crew

## Description

Self-hosted No-Limit Texas Hold'em tournaments for 2 to 8 friends: a poker table rendered in three.js with built-in voice and video chat. There is a single table, and anyone with the URL can join without an account. The UI is available in English and German.

Based on https://github.com/DerKobe/PokerCrew

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Set mode to signin. Click the `Save` button to store your configuration.
1. Start the add-on. 
1. Go to http://homeassistantIP:3000

## Upgrading
1. Upstream does not use releases, so you must monitor `https://github.com/DerKobe/PokerCrew` for updates
1. Uninstall addon
1. ssh into home assistant and run `docker builder prune`
1. Reinstall addon
1. Since this addon builds the docker image from upstream github source, simply rebuilding the addon may not pull down latest source.
1. If no longer works, please create an issue. A required change in the upstream DOCKERFILE will require changes to the addon

[repository]: https://github.com/jdeath/homeassistant-addons


