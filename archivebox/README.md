# Home assistant add-on: ArchiveBox

**ArchiveBox is a powerful, self-hosted internet archiving solution to collect, save, and view sites you want to preserve offline.**

**You can feed it URLs one at a time, or schedule regular imports** from browser bookmarks or history, feeds like RSS, bookmark services like Pocket/Pinboard, and more. See <a href="#input-formats">input formats</a> for a full list.

**It saves snapshots of the URLs you feed it in several formats:** HTML, PDF, PNG screenshots, WARC, and more out-of-the-box, with a wide variety of content extracted and preserved automatically (article text, audio/video, git repos, etc.). See <a href="#output-formats">output formats</a> for a full list.

The goal is to sleep soundly knowing the part of the internet you care about will be automatically preserved in durable, easily accessible formats [for decades](#background--motivation) after it goes down.


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## Key Features


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.


## Configuration
1. ssh into homeassistant
1. type "docker ps" to find container ID of archivebox
1. type "docker exec -it CONTAINERID /bin/bash",
1. type "su archivebox"
1. type "cd /data/archivebox"
1. type "archivebox manage createsuperuser" and enter information
1. type "archivebox config --set SAVE_ARCHIVE_DOT_ORG=False" to set any extra configuration found here: https://github.com/ArchiveBox/ArchiveBox/wiki/Configuration
1. Go to http://localhomeassistantip:8000/ to use webUI. Ingress is not working
1. Use a brookmarklet or browser extension to send links (or all activity) to archivebox


[repository]: https://github.com/jdeath/homeassistant-addons
