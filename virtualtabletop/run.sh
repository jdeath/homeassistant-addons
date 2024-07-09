#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

cd /virtualtabletop-main
cp -n config.template.json /config
cp /config/config.json .
npm start