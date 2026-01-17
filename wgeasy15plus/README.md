# Home assistant add-on: WireGuard Easy

You have found the easiest way to install & manage WireGuard on any Linux host!

This runs version 15 of WG Easy. Ingress does not work. If you need ingress, run the non-15plus version. 

Remember, you need a reverse proxy in front of the UI to be secure. This version enabled non-secure access, but you should not use it unless on your local network.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/wg-easy/wg-easy). 


* All-in-one: WireGuard + Web UI.
* Ingress Not Working for version 15+ (Use my other wgeasy addon, it works fine)! 
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
1. Edit add-on config as needed. Only WG_HOST must be changed to your external IP address
1. Forward WG_PORT (usually 51820) to your home assistant IP from your router
1. Click the `Save` button to store your configuration.

1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI . Ingress does not work, you need to run the non-15plus WireGuard version
1. Make the client configs, scan the QR codes or download the config file.
1. If change settings, you may need to remake the client configs, but it is super simple now!
1. If you want to use a password for the UI, log into your homeassistant and type:
1. I would not recommend exposing this webUI to the internet, but you can if you dare! Use a reverse proxy like caddy to ensure you SSL protect the connection.
   
## Configuration

your configuration will be saved in /addon_configs/2effc9b9_wgeasy15plus

> If want to use Adguard Home Addon https://github.com/hassio-addons/addon-wireguard , set `WG_DEFAULT_DNS` to 172.30.32.1

[repository]: https://github.com/jdeath/homeassistant-addons
