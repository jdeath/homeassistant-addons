#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

MQTT_BROKER=$(jq --raw-output '.MQTT_BROKER // empty' $CONFIG_PATH)
echo "MQTT_BROKER: ${MQTT_BROKER}"
export MQTT_BROKER="${MQTT_BROKER}"

MQTT_PORT=$(jq --raw-output '.MQTT_PORT // empty' $CONFIG_PATH)
echo "MQTT_PORT: ${MQTT_PORT}"
export MQTT_PORT="${MQTT_PORT}"

MQTT_USERNAME=$(jq --raw-output '.MQTT_USERNAME // empty' $CONFIG_PATH)
echo "MQTT_USERNAME: ${MQTT_USERNAME}"
export MQTT_USERNAME="${MQTT_USERNAME}"

MQTT_PASSWORD=$(jq --raw-output '.MQTT_PASSWORD // empty' $CONFIG_PATH)
echo "MQTT_PASSWORD: ${MQTT_PASSWORD}"
export MQTT_PASSWORD="${MQTT_PASSWORD}"

env

flask run --host=0.0.0.0
