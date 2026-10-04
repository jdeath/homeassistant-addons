# Home assistant add-on: Anyworld

## Description
A multiplayer text adventure where you never have to roll dice or keep score — just write what your character does. One player (the host) describes the scenario, then everyone takes turns acting in their own words while an AI weaves every choice into a story that keeps unfolding.

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Start the add-on. It will fail, this is ok
1. go to /addon-configs/2effc9b9_anyworld

save this text as `/addon-configs/2effc9b9_anyworld/config.yaml` and change llm and password variables as appropriate. Refer to `https://github.com/iamarxs/AnyWorld/blob/main/INSTALL.md` for details

```
server:
  host: "0.0.0.0"
  port: 4141
  host_password: host
  player_password: player
llm:
  provider: "compatible"
  endpoint: "http://192.168.1.111:8080/v1"
  model_name: "gemma-4-31B-it-GGUF-MTP"
  initial_output_tokens: 1024
  round_output_tokens: 2048
  dice_output_tokens: 512
  summary_output_tokens: 1024
  token_safety_margin: 256
  request_timeout_seconds: 120.0
  max_retries: 1
  system_prompt: >-
    You are the Dungeon Master of a coherent multiplayer adventure. Resolve all
    players' attempts simultaneously using the supplied authoritative dice and
    established facts. Keep private DM guidance and hidden checks secret; narrate
    only observable consequences. Return the requested structured output.
```

1. Edit `/addon-configs/2effc9b9_anyworld/config.yaml` (see below)
1. Run the addon again and check the logs
1. login at https://homeassistantIP:4141 (you must use https and accept the self signed certificate)


[repository]: https://github.com/jdeath/homeassistant-addons


