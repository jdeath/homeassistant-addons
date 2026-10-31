# Home assistant add-on: Fast SD CPU

## Description
FastSD CPU is a faster version of Stable Diffusion on CPU. Based on Latent Consistency Models , Adversarial Diffusion Distillation and distilled few steps models. 

AI used to add ingress support
_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/homeassistant-addons](https://reporoster.com/stars/jdeath/homeassistant-addons)](https://github.com/jdeath/homeassistant-addons/stargazers)


## Installation

The installation of this add-on is pretty straightforward and not different in
comparison to installing any other Hass.io add-on.

Note: This builds a docker image on your home assistant box. It will take a long time to install all the dependencies. Be patient while it installs.
1. [Add my Hass.io add-ons repository][repository] to your Hass.io instance.
1. Install this add-on.
1. Click the `Save` button to store your configuration.
1. Leave DEVICE as CPU (GPU or NPU not tested).
1. Set MODE to webui or API (MCP crashing on current version)
1. Start the add-on. 
1. Models and results are stored in /addon-configs/2effc9b9_fastsdcpu

Recommend selecting LCM-OpenVINO . On first run, it will download models to /addon-configs/2effc9b9_fastsdcpu

[repository]: https://github.com/jdeath/homeassistant-addons


