# Home assistant add-on: GeoIP Update

The GeoIP Update program performs automatic updates of GeoIP2 and GeoLite2 binary databases.

Desiged to work with @einschmidt Caddy2 Addon for Home Assistant `https://github.com/einschmidt/hassio-addons`

Note: Recent Caddy-2 update (v2.0) changed the config path to `/addon_configs/c80c7555_caddy-2`. If you were running with v1.x, save your configuration of this addon, uninstall, and reinstall, then replace your config but change the directory to above. This is needed because addon has to be rebuilt to be able to see the new directory

Also need a custom caddy binary with `https://github.com/porech/caddy-maxmind-geolocation` setup. Use my `Caddy Builder` addon to make one.

Must setup license key at maxmind.com

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

The Docker image is configured by environment variables. The following
variables are required:

* `GEOIPUPDATE_EDITION_IDS` - List of space-separated database edition IDs.
  Edition IDs may consist of letters, digits, and dashes. default "GeoLite2-ASN GeoLite2-City GeoLite2-Country".

* `GEOIPUPDATE_ACCOUNT_ID` - Your MaxMind account ID (not your username).

* `GEOIPUPDATE_LICENSE_KEY` - Your case-sensitive MaxMind license key (not your password).

* `GEOIPUPDATE_FREQUENCY` - The number of hours between `geoipupdate` runs.
  If this is not set or is set to `0`, `geoipupdate` will run once and exit.

* `GEOIPUPDATE_DB_DIR` - The directory where geoipupdate will download the
  databases. The default is `/addon_configs/c80c7555_caddy-2` to be consistent with new caddy-2 plugin.
  
[repository]: https://github.com/jdeath/homeassistant-addons

## Usage
Make a custom caddy build that includes `--with github.com/porech/caddy-maxmind-geolocation` and put it in `/share/caddy/` (v1.x) with the filename `caddy` or `/addon_configs/c80c7555_caddy-2` (v2.0)

Edit `/share/caddy/Caddyfile`

Add a GEOFilter block to allow certain countries and your local IP address. I found this online, so ask at Caddyforums if you need help.

```
(GEOFILTER) {
        @geofilter {
                not maxmind_geolocation {
                        db_path "/share/caddy/GeoLite2-Country.mmdb"
                        allow_countries IT FR
                }
                not remote_ip private_ranges
        }
        respond @geofilter 403
}
```

Then add this line before any `reverse_proxy` directive
```
import GEOFILTER
```
