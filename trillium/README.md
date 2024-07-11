# Home assistant add-on: Trillium
Trilium Notes is a hierarchical note taking application with focus on building large personal knowledge bases. 
 
 
_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## Features

* Notes can be arranged into arbitrarily deep tree. Single note can be placed into multiple places in the tree (see [cloning](https://github.com/zadam/trilium/wiki/Cloning-notes))
* Rich WYSIWYG note editing including e.g. tables, images and [math](https://github.com/zadam/trilium/wiki/Text-notes#math-support) with markdown [autoformat](https://github.com/zadam/trilium/wiki/Text-notes#autoformat)
* Support for editing [notes with source code](https://github.com/zadam/trilium/wiki/Code-notes), including syntax highlighting
* Fast and easy [navigation between notes](https://github.com/zadam/trilium/wiki/Note-navigation), full text search and [note hoisting](https://github.com/zadam/trilium/wiki/Note-hoisting)
* Seamless [note versioning](https://github.com/zadam/trilium/wiki/Note-revisions)
* Note [attributes](https://github.com/zadam/trilium/wiki/Attributes) can be used for note organization, querying and advanced [scripting](https://github.com/zadam/trilium/wiki/Scripts)
* [Synchronization](https://github.com/zadam/trilium/wiki/Synchronization) with self-hosted sync server
  * there's a [3rd party service for hosting synchronisation server](https://trilium.cc/paid-hosting)
* [Sharing](https://github.com/zadam/trilium/wiki/Sharing) (publishing) notes to public internet
* Strong [note encryption](https://github.com/zadam/trilium/wiki/Protected-notes) with per-note granularity
* Sketching diagrams with built-in Excalidraw (note type "canvas")
* [Relation maps](https://github.com/zadam/trilium/wiki/Relation-map) and [link maps](https://github.com/zadam/trilium/wiki/Link-map) for visualizing notes and their relations
* [Scripting](https://github.com/zadam/trilium/wiki/Scripts) - see [Advanced showcases](https://github.com/zadam/trilium/wiki/Advanced-showcases)
* [REST API](https://github.com/zadam/trilium/wiki/ETAPI) for automation
* Scales well in both usability and performance upwards of 100 000 notes
* Touch optimized [mobile frontend](https://github.com/zadam/trilium/wiki/Mobile-frontend) for smartphones and tablets
* [Night theme](https://github.com/zadam/trilium/wiki/Themes)
* [Evernote](https://github.com/zadam/trilium/wiki/Evernote-import) and [Markdown import & export](https://github.com/zadam/trilium/wiki/Markdown)
* [Web Clipper](https://github.com/zadam/trilium/wiki/Web-clipper) for easy saving of web content


## Installation


1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Make the directory `/share/trillium/` on your homeassistant
1. ssh in to your home assistant and run `chmod 2777 /share/trillium`
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Go to your local homeassistant IP:port admin port or ingress.
1. Follow directions

```
port : 8000 #port you want to run admin interface on.
```

Webui can be found at `<your-ip>:port` or ingress.

[repository]: https://github.com/jdeath/homeassistant-addons
