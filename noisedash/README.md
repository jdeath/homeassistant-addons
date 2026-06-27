# Home assistant add-on: Noisedash

Self-hostable web tool for generating ambient noises

![Noisedash](https://raw.githubusercontent.com/kaythomas0/noisedash/dev/.github/noisedash-screenshot-1.jpg)

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/kaythomas0/noisedash).

* Generate and customize ambient noises and user-uploadable samples (leveraging [Tone.js](https://github.com/Tonejs/Tone.js/))
* Save "noise profiles" so you can easily switch between your created soundscapes. Import and export them for easy sharing, record them for use elsewhere
* Fine-tune your noises with audio processing tools like filters, LFOs, and effects
* Upload and edit audio samples (e.g rain, wind, thunder) to combine with your generated noises. Add effects to them and set playback modes
* Use admin tools to manage multiple users
* Mobile friendly

## Installation

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Quit the add-on and start again (this is necessary to start twice the first time!)
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.

Note: Ingress support required many patches. This could break if upstream dockerfile changes.

## Configuration

```
port : 1432 #port you want to run on.
```

Webui can be found at `<your-ip>:port` or ingress

[repository]: https://github.com/jdeath/homeassistant-addons
