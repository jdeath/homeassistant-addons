# RTLAMR to MQTT Bridge hass.io addon
A hass.io addon for a software defined radio tuned to listen for 433MHz RF transmissions and republish the data via MQTT

This hassio addon is based on biochemguy's (non-docker) setup: https://community.home-assistant.io/t/get-your-smart-electric-water-and-gas-meter-scm-readings-into-home-assistant-with-a-rtl-sdr
This hass.io addon is based on James Fry' project here: https://github.com/james-fry/hassio-addons/tree/master/rtl4332mqtt
which was based on Chris Kacerguis' project here: https://github.com/chriskacerguis/honeywell2mqtt,
which is in turn based on Marco Verleun's rtl2mqtt image here: https://github.com/roflmao/rtl2mqtt

Try some of my other addons at: https://github.com/jdeath/homeassistant-addons
Currently have MeTube (youtube downloader), speedtest, emulatorjs (web based retro game console player)

_Thanks to everyone having starred my repo! To star it click on the image below, then it will be on top right. Thanks!_

[![Stargazers repo roster for @jdeath/RTLAMR2MQQT](https://reporoster.com/stars/jdeath/RTLAMR2MQQT)](https://github.com/jdeath/RTLAMR2MQQT/stargazers)

## Usage

1) Install the addon. Do this by either:
 - downloading this repository and adding in a folder under /addons/ (eg. /addons/rtlamr2mqtt)
 - adding this respository to the Add-on Store

2) Use addon configuration to configure:
- mqtt_host (use number IP address, not hassio.local, localhost, 127.0.0.1, etc) . Also do not add port number here
- mqtt_port
- mqtt_user
- mqtt_password
- msgType
- ids

3) Copy rtl2mqtt.sh to your hass.io config dir in a subdir called rtlamr2mqtt.
i.e.
.../config/rtlamr2mqtt/rtl2mqtt.sh
This allows you to edit the start script if you need to make any changes.

If you are using a 64 bit version of hassio, add below line into the rtl2mqtt.sh:
```
export LD_LIBRARY_PATH=/usr/local/lib64
```

If this is using too much processor, add the -duration=60s (or how every many seconds you want) tag to your the rtl2mqqt.sh script. Turns out rtlamr uses quite a bit of processor:
```
/go/bin/rtlamr -format json -msgtype=$MQTT_MSGTYPE -filterid=$MQTT_IDS -duration=60s | while read line
```
also increase the sleep to however many seconds you want to wait until scanning again. I am using 60s of processing, then 5 mintutes (300s) of sleeping.

NOTE that some people have reported issues using samba to copy the script. For some reason it does not get copied to the container on start up of the addon. If you see this issue, please scp the script to your hassio config folder, or ssh in and edit the file locally with vi/nano.


4) Start the addon


## MQTT Data

Data to the MQTT server is based on biochemguy setup: readings/$DEVICEID/meter_reading

## Hardware

This has been tested and used with the following hardware (you can get it on Amazon)

- NooElec NESDR Nano 2+ Tiny Black RTL-SDR USB
- RTL-SDR Blog R820T2 RTL2832U 1PPM TCXO SMA Software Defined Radio


## Troubleshooting

If you see this error:

> Kernel driver is active, or device is claimed by second instance of librtlsdr.
> In the first case, please either detach or blacklist the kernel module
> (dvb_usb_rtl28xxu), or enable automatic detaching at compile time.

Then run the following command on the host

```bash
sudo rmmod dvb_usb_rtl28xxu rtl2832
```
