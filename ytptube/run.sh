#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
YTP_REMOVE_FILES=false
YTP_REMOVE_FILES=$(jq --raw-output '.YTP_REMOVE_FILES' $CONFIG_PATH)
echo "YTP_REMOVE_FILES: ${YTP_REMOVE_FILES}"
export YTP_REMOVE_FILES="${YTP_REMOVE_FILES}"

YTP_DOWNLOAD_PATH=$(jq --raw-output '.YTP_DOWNLOAD_PATH' $CONFIG_PATH)
echo "YTP_DOWNLOAD_PATH: ${YTP_DOWNLOAD_PATH}"
export YTP_DOWNLOAD_PATH="${YTP_DOWNLOAD_PATH}"

/opt/python/bin/python /app/app/main.py --ytp-process
