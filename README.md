# homeassistant-addons

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://git-lister.onrender.com/api/stars/jdeath/homeassistant-addons?limit=30)](https://github.com/jdeath/homeassistant-addons/stargazers)

## About

Home Assistant allows anyone to create add-on repositories to share their
add-ons for Home Assistant easily. This repository is one of those repositories,
providing extra Home Assistant add-ons for your installation.

The primary goal of this project is to provide you (as a Home Assistant user)
with additional, high quality, add-ons that allow you to take your automated
home to the next level.

## Installation

[![Add repository on my Home Assistant][repository-badge]][repository-url]

If you want to do add the repository manually, please follow the procedure highlighted in the [Home Assistant website](https://home-assistant.io/hassio/installing_third_party_addons). Use the following URL to add this repository: https://github.com/jdeath/homeassistant-addons

MeTube from https://github.com/alexta69/metube
Make a directory /share/metube or may not work correctly. Files will download into this directory

Speedtest from https://hub.docker.com/r/e7db/speedtest

Emulator JS from https://github.com/linuxserver/emulatorjs
Make a directory /share/emulatorjs

WireGuard Easy based on https://github.com/WeeJeWel/wg-easy/
Make a directory /ssl/wgeasy

[repository-badge]: https://img.shields.io/badge/Add%20repository%20to%20my-Home%20Assistant-41BDF5?logo=home-assistant&style=for-the-badge
[repository-url]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fjdeath%2Fhomeassistant-addons

## How to use Playwright JS enabled fetcher instead of built in Plaintext/HTTP Client

The Changedetection.io addon by itself can only fetch websites using a built in Plaintext/HTTP Client.

Many modern web pages use JavaScript to fill-in the content, they are more dynamic and sometimes need a real chrome browser for fetching the content, although many may work with our built in 'fetcher'

You can configure Changedetection.io to fetch pages using the Playwright, otherwise it will fetch using a plain non-JS built in browser.
Using the Playwright fetcher offers the full Changedetection.io functionality, incl. JS Browser steps to fetch content and Visual Filter Selector.

To use the Playwright fetcher Changedetection.io addon needs to team up with the Browserless Chrome addon made by alexbelgium.

To Install the Browserless Chrome addon, add the alexbelgium/hassio-addons repository (https://github.com/alexbelgium/hassio-addons/) in Homeassistant.
Install and start the addon from the Homeassistant Interface.
To use the Playwright fetcher simply check "Playwright Chromium/Javascript" it in the "Request" tab when adding a new site to be monitored or to set it as system standard for all monitored Sites, go to the Webinterface of your Changedetection.io addon > Settings > Fetching and select "Playwright Chromium/Javascript".

More on Browserless Chrome addon: https://github.com/alexbelgium/hassio-addons/tree/master/browserless_chrome

Both addons need to run on the same machine.
Tested on Home Assistant 2023.5.3/Supervisor 2023.04.1/Operating System 10.1 on a Raspberry Pi 4B, but should work with any other Version and with amd64 devices as well.

Note: Browserless Chrome addon is quite ressource hungry when fetching websites, bot in terms of RAM an CPU. Works fine on RPi 4B, may be slow on older devices. Maximum simultaneous fetches are limited to 1.
