# Home assistant add-on: Leto Reader
**LetoReader** is a versatile speed reader designed to enhance your reading efficiency. It supports high-speed reading for skimming or consuming easy texts at e.g. 400-1000 words per minute. However, it can also be used at lower speeds for better comprehension while still benefiting from Rapid Serial Visual Presentation (RSVP).

### Key differences to traditional reading
- Fixed reading speed (configurable by the user)
- Suppression of subvocalization and regressive saccades at higher speeds
- Less eye fatigue

### Features
- Chunking, pacing and highlighting built in
- Great UX and responsive design
- radically minimal user interface
- Easy importing
- Customizable (8 settings)
- Focus mode (for dyslexia/add/adhd)
- No external API dependencies
- Local-only storage
- FOSS
- Self-hostable

#### Import options
- From a URL
- uploading a file (.pdf, .md, .txt, .html, .epub)
- Clipboard
- Request body of GET request



_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/Axym-Labs/LetoReader).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on. 
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
