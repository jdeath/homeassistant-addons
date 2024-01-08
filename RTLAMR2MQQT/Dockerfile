# Docker file to create an image for a hass.io add-on that contains enough software to listen to events via RTL_SDR/RTL_433 and then publish them to a MQTT broker.
# The script resides in a volume and can be modified to meet your needs.
# This hass.io addon is based on Chris Kacerguis' project here: https://github.com/chriskacerguis/honeywell2mqtt,
# which is in turn based on Marco Verleun's rtl2mqtt image here: https://github.com/roflmao/rtl2mqtt

# IMPORTANT: The container needs privileged access to /dev/bus/usb on the host.

ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

MAINTAINER jaaem

LABEL Description="This image is used to start a script that will monitor for RF events on 433Mhz (configurable) and send the data to an MQTT server"

#
# First install software packages needed to compile rtl_433 and to publish MQTT events
#
RUN apk add --no-cache --virtual build-deps alpine-sdk cmake git libusb-dev && \
    mkdir /tmp/src && \
    cd /tmp/src && \
    git clone https://github.com/osmocom/rtl-sdr.git && \
    mkdir /tmp/src/rtl-sdr/build && \
    cd /tmp/src/rtl-sdr/build && \
    cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON -DCMAKE_INSTALL_PREFIX:PATH=/usr/local && \
    make && \
    make install && \
    chmod +s /usr/local/bin/rtl_* && \
    apk del build-deps && \
    rm -r /tmp/src && \
    apk add --no-cache libusb mosquitto-clients jq coreutils wget make musl-dev go git gcc usb-modeswitch

# Configure Go
ENV GOROOT /usr/lib/go
ENV GOPATH /go
ENV PATH /go/bin:$PATH
RUN mkdir -p ${GOPATH}/src ${GOPATH}/bin

RUN go install github.com/bemasher/rtlamr@latest

#
# Define an environment variable
#
# Use this variable when creating a container to specify the MQTT broker host.
ENV MQTT_HOST="hassio.local"
ENV MQTT_PORT="1883"
ENV MQTT_USER="guest"
ENV MQTT_PASS="guest"
ENV MQTT_TOPIC="homeassistant/sensor/rtl433"

CMD cd / && cp /config/rtlamr2mqtt/rtl2mqtt.sh /rtl2mqtt.sh && chmod +x /rtl2mqtt.sh && /rtl2mqtt.sh
