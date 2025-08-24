# Home assistant add-on: ytptube

Web GUI for yt-dlp with playlist & channel support (https://github.com/arabcoders/ytptube).


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://github.com/arabcoders/ytptube).

# YTPTube Features.

* Multi-downloads support.
* Random beautiful background. `can be disabled or source changed`.
* Can handle live streams.
* Scheduler to queue channels or playlists to be downloaded automatically at a specified time.
* Send notification to targets based on selected events. 
* Support per link `cli options` & `cookies`.
* Queue multiple URLs separated by comma.
* Presets system to re-use frequently used yt-dlp options.
* Simple file browser. `Disabled by default`.
* A built in video player **with support for sidecar external subtitles**.
* New `POST /api/history` endpoint that allow one or multiple links to be sent at the same time.
* New `GET /api/history/add?url=http://..` endpoint that allow to add single item via GET request.
* Modern frontend UI.
* SQLite as database backend.
* Basic authentication support.
* Support for curl_cffi, see [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#impersonation)
* Support basic mode for WebUI for non-technical users, which hides most of the normal features from view.
* Bundled tools in container: curl-cffi, ffmpeg, ffprobe, aria2, rtmpdump, mkvtoolsnix, mp4box.
* Automatic upcoming live stream re-queue.
* Apply `yt-dlp` options per custom defined conditions.
* Custom browser extensions, bookmarklets and iOS shortcuts to send links to YTPTube instance.

## Installation

The installation of this add-on has a few extra steps.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Download directory defaults to /share/ytptube, can be changed to anything in share
1. Start the add-on. It will fail
1. ssh into home assistant and type `chown hassio /addon_configs/2effc9b9_ytptube`
1. Start the add-on. It will fail
1. ssh again into home assistant and type `chown hassio /share/ytptube` or the download directory if you changed it
1. Start the add-on
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI via <your-ip>:port. Ingress does not work
1. Click "Rebuild" will pull in the latest yt-dlp, even if YTPTube does not have an update.
## Configuration

```
port : 8081 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
