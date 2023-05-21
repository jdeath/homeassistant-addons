# Home assistant add-on: Changedetection.io

**The best and simplest self-hosted free open source website change detection tracking, monitoring and notification service. An alternative to Visualping, Watchtower etc. Designed for simplicity - the main goal is to simply monitor which websites had a text change for free. Free Open source web page change detection**

#### Example use cases

- Products and services have a change in pricing
- _Out of stock notification_ and _Back In stock notification_
- Governmental department updates (changes are often only on their websites)
- New software releases, security advisories when you're not on their mailing list.
- Festivals with changes
- Realestate listing changes
- Know when your favourite whiskey is on sale, or other special deals are announced before anyone else
- COVID related news from government websites
- University/organisation news from their website
- Detect and monitor changes in JSON API responses 
- JSON API monitoring and alerting
- Changes in legal and other documents
- Trigger API calls via notifications when text appears on a website
- Glue together APIs using the JSON filter and JSON notifications
- Create RSS feeds based on changes in web content
- Monitor HTML source code for unexpected changes, strengthen your PCI compliance
- You have a very sensitive list of URLs to watch and you do _not_ want to use the paid alternatives. (Remember, _you_ are the product)

_Need an actual Chrome runner with Javascript support? We support fetching via WebDriver and Playwright!</a>_

#### Key Features

- Lots of trigger filters, such as "Trigger on text", "Remove text by selector", "Ignore text", "Extract text", also using regular-expressions!
- Target elements with xPath and CSS Selectors, Easily monitor complex JSON with JsonPath rules
- Switch between fast non-JS and Chrome JS based "fetchers"
- Easily specify how often a site should be checked
- Execute JS before extracting text (Good for logging in, see examples in the UI!)
- Override Request Headers, Specify `POST` or `GET` and other methods
- Use the "Visual Selector" to help target specific elements

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)

## Key Features


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Go to ip:port . Ingress sorta works, but page does not render correctly


## How to use Playwright JS enabled fetcher instead of built in Plaintext/HTTP Client

The Changedetection.io addon by itself can only fetch websites using a built in Plaintext/HTTP Client.

Many modern web pages use JavaScript to fill-in the content, they are more dynamic and sometimes need a real chrome browser for fetching the content, although many may work with the built in 'fetcher'

You can configure Changedetection.io to fetch pages using the Playwright fetcher, otherwise it will fetch using a plain non-JS built in browser. Using the Playwright fetcher offers the full Changedetection.io functionality, incl. JS Browser steps to fetch content and Visual Filter Selector.

To use the Playwright fetcher, Changedetection.io addon needs to team up with the Browserless Chrome addon made by alexbelgium.

To Install the Browserless Chrome addon, add the alexbelgium/hassio-addons repository (https://github.com/alexbelgium/hassio-addons/) in Homeassistant. Install and start the addon from the Homeassistant Interface. To use the Playwright fetcher simply check "Playwright Chromium/Javascript" it in the "Request" tab when adding a new site to be monitored or to set it as system standard for all monitored Sites, go to the Webinterface of your Changedetection.io addon > Settings > Fetching and select "Playwright Chromium/Javascript".

More on Browserless Chrome addon: https://github.com/alexbelgium/hassio-addons/tree/master/browserless_chrome

Both addons need to run on the same machine. Tested on Home Assistant 2023.5.3/Supervisor 2023.04.1/Operating System 10.1 on a Raspberry Pi 4B, but should work with any other Version and with amd64 devices as well.

Note: Browserless Chrome addon is quite ressource hungry when fetching websites, bot in terms of RAM and CPU. Works fine on RPi 4B, may be slow on older devices. Maximum simultaneous fetches are limited to 1.


[repository]: https://github.com/jdeath/homeassistant-addons
