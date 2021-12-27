# Home assistant add-on: Scribble-rs

Scribble.rs is an alternative to the web-based drawing game skribbl.io. My main problems with skribbl.io were the ads and the fact that a disconnect would cause you to lose your points. On top of that, the automatic word choice was quite annoying and caused some frustration.


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on https://github.com/scribble-rs/scribble.rs.

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.

## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.
