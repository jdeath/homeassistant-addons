# Home assistant add-on: WireGuard Easy Version 15+

You have found the easiest way to install & manage WireGuard on any Linux host!

This runs version 15+ of WG Easy with Home Assistant ingress support.

Remember, you need a reverse proxy in front of the UI to be secure. This version enables non-secure access for setup, but you should not use it unless on your local network.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/wg-easy/wg-easy). 


* All-in-one: WireGuard + Web UI.
* Ingress support via HA sidebar.
* Easy installation, simple to use.
* List, create, edit, delete, enable & disable clients.
* Show a client's QR code.
* Download a client's configuration file.
* Statistics for which clients are connected.
* Tx/Rx charts for each connected client.
* Gravatar support.

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Set your ports (or leave the default)
1. Forward the TCP and UDP ports on your router. Forward the same ports, do not try to make them different.
1. Start the addon. This addon takes a while to start. Give it time and hit reload a few times
1. To setup the addon, you must first go to non-Ingress and change the URL
1. To to `http://HomeAssistantIPAddress:Port/` (port will probably be 51821)
1. It will reload the URL to something like `http://192.168.1.XXX:51821/login`
1. Remove `login` and make it `setup/1`
1. Go through the wizard and set everything up
1. Close the web browser tab
1. Go back to home assistant apps.
1. Open WebUI (ingress) or directly at port 51821
1. Enter your login and should work like normal
1. If you go to http://port:ip and cannot login, make sure url looks like `http://192.168.1.XXX:51821/login`
1. If you messed something up. shutdown app, clear `/addon_configs/2effc9b9_wgeasy15plus`, restart, and do the `setup/1` trick
   
## Configuration

your configuration will be saved in /addon_configs/2effc9b9_wgeasy15plus

> If want to use Adguard Home Addon https://github.com/hassio-addons/addon-wireguard , set DNS to 172.30.32.1

[repository]: https://github.com/jdeath/homeassistant-addons
