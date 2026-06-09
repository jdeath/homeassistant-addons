# Home assistant add-on: degoog

Search aggregator that queries multiple engines and shows results in one place. You can add custom search engines, bang-command plugins, slot plugins (query-triggered panels above/below results or in the sidebar), and transports (custom HTTP fetch strategies like curl, FlareSolverr, or your own). The dream would be to eventually have a user made marketplace for plugins/engines.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon uses the [docker image](https://github.com/degoog-org/degoog).

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI — accessible via Home Assistant ingress (side panel) or `<your-ip>:4445`.

## Configuration
data files in \addon_configs\2effc9b9_degoog\
```
port : 4445 #port you want to run on. Cannot be 4444
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
