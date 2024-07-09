# Home assistant add-on: VirtualTabletop

VTT is an open-source, free to use platform for creating and playing games.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on https://github.com/ArnoldSmith86/virtualtabletop. 

This project aims to create a virtual tabletop in the browser where you can (re)create all board, dice and card games and play them without registration over the internet.

You can host your own instance or go to [VirtualTabletop.io](https://virtualtabletop.io).

This project is inspired by [playingcards.io](https://playingcards.io).

This project aims to be able to import PCIO files and have them be immediately playable.

## Installation

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Start the add-on.
1. It will fail, that is ok.
1. Go to \\addon_configs\2effc9b9_virtualtabletop
1. rename config.template.json to config.json
1. edit config.json and enter the IP address of your local machine or the IP address of how you reverse proxy your machine.
1. Restart addon
1. Go to IP address.
