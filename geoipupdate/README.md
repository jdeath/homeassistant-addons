# Home assistant add-on: GeoIP Update

The GeoIP Update program performs automatic updates of GeoIP2 and GeoLite2 binary databases.

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
  databases. The default is `/share/caddy`.
  
[repository]: https://github.com/jdeath/homeassistant-addons
