# Home assistant add-on: Wedding Share

WeddingShare is a very basic site with only one goal. It provides you and your guests a way to share memories of and leading up to the big day. Simply provide your guests with a link to a gallery either via a Url or even better by printing out the provided QR code and dropping it on your guests dinner tables. Doing so will allow them to view your journey up to this point such as dress/suit shopping, viewing the venue, doing the food tasting or cake shopping, etc. You are not limited to a single gallery. You can generate multiple gallerys all with their own sharable links. At this stage galleries are a bit unsecure, meaning anyone with the link has acess to view and share images so I recommend keeping your share links private. To combat strangers gaining access to your galleries you can provide a secret key during setup but be advised this is a deterant to make guessing Urls slightly harder and not an actual security catch all.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/Cirx08/WeddingShare).

## Installation

1. Consult the official [repo](https://github.com/Cirx08/WeddingShare)
1. Most options in official documentation are supported, except for secret key
1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Set the options under configuration tab
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port
1. Consult official documentation to make a jsdos bundle. It is kind of a pain!
1. Upload your bundle and play your game.
1. Settings will be in /addon_configs/2effc9b9_weddingshare
## Configuration

```
port : 5000 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
