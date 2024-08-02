# Home assistant add-on: Readeck

Readeck is a simple web application that lets you save the precious readable content of web pages you like and want to keep forever. See it as a bookmark manager and a read later tool.


_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

This addon is based on the [docker image](https://codeberg.org/readeck/readeck).

## Features

### 🔖 Bookmarks

Like a page you're reading? Paste the link in Readeck and you're done!

### 📸 Articles, pictures and videos

Readeck saves the readable content of web pages for you to read later. It also detects when a page is an image or a video and adapts its process accordingly.

### ⭐ Labels, favorites, archives

Move bookmarks to archives or favorites and add as many labels as you want.

### 🖍️ Highlights

Highlight the important content of your bookmarks to easily find it later.

### 🗃️ Collections

If you need a dedicated section with all your bookmarks from the past 2 weeks labeled with "cat", Readeck lets you save this search query into a collection so you can access it later.

### 🧩 Browser Extension

Want to keep something for later while browsing? No need to copy and paste a link. Install the browser extension and save bookmarks in one click!

- [For Mozilla Firefox](https://addons.mozilla.org/en-US/firefox/addon/readeck/)
- [For Google Chrome](https://chromewebstore.google.com/detail/readeck/jnmcpmfimecibicbojhopfkcbmkafhee)
- [More Information and Source Code](https://codeberg.org/readeck/browser-extension)

### 📖 E-Book export

What's best than reading your collected articles on your e-reader? You can export any article to an e-book file (EPUB). You can even export a collection to a single book!

On top of that, you can directly access Readeck's catalog and collections from your e-reader if it supports OPDS.

### 🔎 Full text search

Whether you need to find a vague piece of text from an article, or all the articles with a specific label or from a specific website, we've got you covered!

### 🚀 Fast!

Readeck is a modern take on so called boring, but proven, technology pieces. It guaranties very quick response times and a smooth user experience.

### 🔒 Built for your privacy and long term archival

Will this article you like be online next year? In 10 year? Maybe not; maybe it's all gone, text and images. For this reason, and for your privacy, text and images are all stored in your Readeck instance the moment you save a link.

With the exception of videos, not a single request is made from your browser to an external website.


## Installation

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Quit the add-on and start again (this is necessary to start twice the first time!)
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.

## Updating
Because the source code is not hosted on github, very hard to automatically update this. Click "Rebuild" and it should pull in the latest version of readeck
## Configuration

```
port : 8000 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.

[repository]: https://github.com/jdeath/homeassistant-addons
