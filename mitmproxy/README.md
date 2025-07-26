# Home assistant add-on: mitmproxy

Mitmproxy is your swiss-army knife for debugging, testing, privacy measurements, and penetration testing. It can be used to intercept, inspect, modify and replay web traffic such as HTTP/1, HTTP/2, WebSockets, or any other SSL/TLS-protected protocols. You can prettify and decode a variety of message types ranging from HTML to Protobuf, intercept specific messages on-the-fly, modify them before they reach their destination, and replay them to a client or server later on. 

Use mitmproxy's main features in a graphical interface with mitmweb. Do you like Chrome's DevTools? mitmweb gives you a similar experience for any other application or device, plus additional features such as request interception and replay. 

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/mitmproxy/mitmproxy).


## Installation

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration for proxy port and webUI port.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Your certificates will be generated in /addon_configs/2effc9b9_mitmproxy
1. If you have certificates from another install, copy them to this directory instead.
1. Open WebUI should work via <your-ip>:port.
1. The password is `homeassistant`


Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
