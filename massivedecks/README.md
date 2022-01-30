# Home assistant add-on: Massive Decks
Massive Decks is a free, open source comedy party game based on Cards against Humanity. Play with friends!

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## Features

 - Play together in the same room or online.
 - Use any device (Phone, PC, Chromecast, anything with a web browser).
 - You can set up a central screen, but you don't need to (no need to stream anything for other players online).
 - Custom decks (via [Many Decks][many-decks]).
 - Customise the rules:
   - Custom cards.
   - House rules.
   - AI players.
   - Custom time limits if you want them.
 - Spectators.
 - Keeps your game private by default, you can also set a game password if needed.
 - Community translations.

[many-decks]: https://decks.rereadgames.com/

## About

Based on https://github.com/Lattyware/massivedecks/

The game is open source software available under [the AGPLv3 license](LICENSE).

## Installation

This addon takes a while to build. This is because massivedecks splits server/client into two dockers and this addon merges those those manually from source!

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. Install this add-on (Will take a while to build).
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should load on IP:port
