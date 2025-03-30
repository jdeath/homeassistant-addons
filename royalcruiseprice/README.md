# Home assistant add-on: Royal Cruise Price

## Description
Automatically check your cruise price. If you want to price out excursions, see my other addon

This uses an included version of chrome, so limited to amd64 installations. Required because Royal Caribbean uses dynamic javascript to display the cruise price

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Start the add-on. It will fail, this is ok
1. go to /addon-configs/2effc9b9_royalcruiseprice
1. Edit the configCruise.yaml with your cruise info (see below)
1. Run the addon again and check the logs
1. After confirmed working, use an automation to run this once a day


## Configure configCruise.yaml

```
cruises:
  - cruiseURL: "https://www.royalcaribbean.com/checkout/guest-info?sailDate=2025-12-27&shipCode=VI&groupId=VI12BWI-753707406&packageCode=VI12L049&selectedCurrencyCode=USD&country=USA&cabinClassType=OUTSIDE&roomIndex=0&r0a=2&r0c=0&r0b=n&r0r=n&r0s=n&r0q=n&r0t=n&r0d=OUTSIDE&r0D=y&rgVisited=true&r0C=y&r0e=N&r0f=4N&r0g=BESTRATE&r0h=n&r0j=2138&r0w=2&r0B=BD&r0x=AF&r0y=6aa01639-c2d8-4d52-b850-e11c5ecf7146"
    cruiseXPath: "//div[@data-testid='funnel-footer-total-price']"
    paidPrice: "3612.12"
  - cruiseURL: "url2"
    cruiseXPath: "//div[@data-testid='funnel-footer-total-price']"
    paidPrice: "3612.12"	

apprise:
  - url: "hassio://192.168.1.14/XXXXX"
  - url: "mailto://user:XXXX@gmail.com"
```

To get the cruise URL:
1. Go to Royal Caribbean and do a mock booking of the room you have
1. Select a cruise and Select your room type/room and complete until they ask for your personal information.
1. At this point, you should see a blue bar at the bottom right of webpage with a price
1. Copy the URL into the cruiseURL field. Remove the last "&r0A=XXXX.XX" which encodes the current price
1. The cruiseXPath should be default, but I leave it configurable in case royal changes the website
1. put the price you paid in the paidPrice field
1. Run the addon and see if it works
1. you can add multiple cruiseURL/cruiseXPath/paidPrice to track multiple cruises
1. If it is lower than you paid for and before final payment date, call your Travel Agent or Royal Caribbean (if you booked direct) and they will reduce the price
## Automatic Running
1. Create an automation to run this addon once a day (at a random time to avoid ban)

```
alias: Start Cruise Price Check
description: ""
trigger:
  - platform: time
    at: "05:00:00"
condition: []
action:
  - delay: "{{ (range(0, 1)|random|int) }}:{{ (range(1, 59)|random|int) }}:00"
  - service: hassio.addon_start
    data:
      addon: 2effc9b9_royalcruiseprice
mode: single
```

# Sending a notification.
1. edit `/addon-configs/2effc9b9_royalcruiseprice/config.yaml`
1. Configure the line for a notification

It should look something like this for homeassistant notification:
```
# config.yaml
apprise:
  urls:
    - 'hassio://192.168.X.XX/eyXXXXXXXXXXXXXXXX.eyXXXXXXXXXXXXXXXXXxx'
```
Where the `eyXXX.eyXXX` string is a Home Assistant Long-Lived Token. Long-lived access tokens can be created using the "Long-Lived Access Tokens" section at the bottom of a user's Home Assistant profile page.

More details here: `https://github.com/caronc/apprise/wiki/Notify_homeassistant`

# Add To Sidebar
Since there is no WebUI, this cannot be shown in the sidebar. However you can add the following code to your Home Assistant `configuration.yaml` to show the log via a sidebar entry

```
panel_custom:
  - name: panel_rewards
    sidebar_title: Rewards
    sidebar_icon: mdi:medal
    url_path: 'hassio/addon/2effc9b9_royalcruisecheck/logs'
    module_url: /api/hassio/app/entrypoint.js
    embed_iframe: true
    require_admin: true
```

# Issues


[repository]: https://github.com/jdeath/homeassistant-addons
