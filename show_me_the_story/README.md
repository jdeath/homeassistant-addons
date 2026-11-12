# Home assistant add-on: Show Me The Story

RA local application for writing long fiction with AI. One executable and a browser interface connect to an OpenAI-compatible model service to manage settings, plan batches of chapters, draft and revise prose, and export your work.

**The complete application ships as a single executable under 5 MB**—small enough to download, move, and keep anywhere.

You decide the story’s rules and direction. Those rules may be realistic or entirely fictional.


## First run

1. Download a release for your system, extract it into a directory you intend to keep, and launch it.
2. Open `http://homeassistantip:48090` and create a Chinese or English project.
3. In Configuration, enter the API address, model identifier, and API key. Test the connection and save. Use the exact model identifier supplied by your provider.
4. Save the genre, target chapter length, style, and point of view. Add essential characters and worldview entries.
5. In Outline, enter a synopsis and chapter count (1–36) for the first batch. Generate and review it. If the page offers Confirm outline, confirm before writing.
6. In Writing, generate one chapter, read and revise it, then accept it before continuing.

Start with a small batch and auto-confirm disabled to check the voice, characters, and model behavior.

Based on: https://github.com/Nigh/show-me-the-story/

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on.
1. Check the logs of the add-on to see if everything went well.
1. Open WebUI should work via ingress or <your-ip>:port.

## Configuration

```
port : 8081 #port you want to run on.
```

Webui can be found at `<your-ip>:port`.


[repository]: https://github.com/jdeath/homeassistant-addons
