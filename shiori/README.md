# Home assistant add-on: Shiori
 Shiori is a simple bookmarks manager written in the Go language. Intended as a simple clone of Pocket. You can use it as a command line application or as a web application. 
 
Detailed information at: https://github.com/go-shiori/shiori/ 

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## Features

- Basic bookmarks management i.e. add, edit, delete and search.
- Import and export bookmarks from and to Netscape Bookmark file.
- Import bookmarks from Pocket.
- Simple and clean command line interface.
- Simple and pretty web interface for those who don't want to use a command line app.
- Portable, thanks to its single binary format.
- Support for sqlite3, PostgreSQL and MySQL as its database.
- Where possible, by default `shiori` will parse the readable content and create an offline archive of the webpage.
- Beta: support for Firefox and Chrome.


## Installation


1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. To run command line shiori commands:
1. ssh into homeassistant
1. type "docker ps" to find container ID of shiori
1. type "docker exec -it CONTAINERID command", 
1. Go to your local homeassistant IP:port admin port.
1. default login: shiori, pass: gopher
1. Create a new user and default will be removed
1. Your data is stored in a
## Configuration
1. Create new bookmarks in the web interface or setup a browser extension
1. To import existing bookmarks, you need to manually ssh in
1. Copy your bookmarks.html from your browser into homeassistant /addon_configs/2effc9b9_shiori/
1. Follow ssh instructions into the docker:
1. ssh into homeassistant
1. type "docker ps" to find container ID of shiori
1. type "docker exec -it CONTAINERID shiori import /config/bookmarks.html", 
```
port : 8000 #port you want to run admin interface on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
