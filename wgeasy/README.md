# Home assistant add-on: WireGuard Easy

You have found the easiest way to install & manage WireGuard on any Linux host!

**Issue: If add-on will not start, make sure WG_POST_UP, WG_POST_DOWN is set to "" in the YAML or blank in the UI. There was a error after a recent update.**

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/wg-easy/wg-easy). The src has been slightly modified from WeeJeWel/wg-easy to allow ingress and custom Wireguard config location. I rehost this code locally so rebuilding automatically pulls in the latest version of wireguard but not any changes to the UI from WeeJeWel/wg-easy.


* All-in-one: WireGuard + Web UI.
* Ingress working 
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
1. Forward WG_PORT (usually 51820) to your homeassistat IP from your router
1. Click the `Save` button to store your configuration.
1. Make the directory /ssl/wgeasy to store your configuration. (make different directory if change WGPATH in the addon-on config)
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should load via ingress
1. Make the client configs, scan the QR codes or download the config file.
1. If change settings, you may need to remake the client configs, but it is super simple now!
1. If you want to use a password for the UI, log into your homeassistant and type:
   `docker run -it ghcr.io/wg-easy/wg-easy wgpw YOUR_PASSWORD`
1. Copy everything between the single quotes and put into the PASSWORD_HASH field. Since the UI is available via ingress, not really needed. I would not recommend exposing this webUI to the internet, but you can if you dare!
## Configuration

| Env | Default | Example | Description |
| - | - | - | - |
| `PASSWORD_HASH` | - | `$2a$12$XC....` | When set, requires a password when logging in to the Web UI. See above |
| `WG_HOST` | - | `vpn.myserver.com` | The public hostname of your VPN server. |
| `WG_PORT` | `51820` | `12345` | The public UDP port of your VPN server. WireGuard will always listen on `51820` inside the Docker container. Not used >v14|
| `WG_CONFIG_PORT` | `51820` | `12345` | The UDP port used on Home Assistant Plugin. The public UDP port of your VPN server. Make sure network port is the same in home assistant network config |
| `WG_DEVICE` | `eth0` | `eno1` | Ethernet device the wireguard traffic should be forwarded through. Should not be needed |
| `WG_PATH` | `/ssl/wgeasy` | `/share/wgeasy` | Persistant storage location on homeassistant |
| `WG_PERSISTENT_KEEPALIVE` | `0` | `25` | Value in seconds to keep the "connection" open. |
| `WG_DEFAULT_ADDRESS` | `10.8.0.x` | `10.6.0.x` | Clients IP address range. |
| `WG_DEFAULT_DNS` | `1.1.1.1` | `8.8.8.8, 8.8.4.4` | DNS server clients will use. |
| `WG_ALLOWED_IPS` | `0.0.0.0/0, ::/0` | `192.168.15.0/24, 10.0.1.0/24` | Allowed IPs clients will use. |
| `WG_POST_UP` | `...` | `iptables ...` | See [config.js](https://github.com/WeeJeWel/wg-easy/blob/master/src/config.js#L19) for the default value. |
| `WG_POST_DOWN` | `...` | `iptables ...` | See [config.js](https://github.com/WeeJeWel/wg-easy/blob/master/src/config.js#L26) for the default value. |

> If you change `WG_PORT`, make sure to also change the exposed port.

> If want to use Adguard Home Addon https://github.com/hassio-addons/addon-wireguard , set `WG_DEFAULT_DNS` to 172.30.32.1

[repository]: https://github.com/jdeath/homeassistant-addons
