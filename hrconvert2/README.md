# Home assistant add-on: HRConvert2

- Converts 445 different file formats.
- Self hosted. Installs on a home server!
- All conversions are performed locally on your server.
- Performs Optical Character Recognition (OCR) on PDFs & images.
- Can scan files for viruses automatically in the background with ClamAV.
- Allows users to scan files for viruses on-demand using ClamAV or [zelon88/scanCore](https://github.com/zelon88/scanCore).
- Allows users to generate temporary links for sharing files.
- Minimalistic drag & drop interface.
- Each user gets their own temporary scratch space!
- End users can switch between 13 languages by appending it to the URL like this: `?language=en`
- Safe enough for public facing environments (when properly implemented).
- No databases. No cookies. No cache files. 
- Installs cleanly alongside other popular software (like WordPress).
- Does not make external connections.
- All JS is locally installed. No bulky frameworks. No analytics. No Google Fonts.
- No tracking capabilities whatsoever.
- Comes with 4 color schemes set in config.php.
- Secure, performant, & compact codebase that's been open-source for years.

Image is 2 GB, so will take a long time to install, be patient.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/5etools-mirror-2/5etools-mirror-2.github.io).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on. 2 GB image will take a while to download
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via <your-ip>:port.

## Configuration

```
port : 8080 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
