#!/bin/bash
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

# Username and password for SilverBullet user
SB_USER=$(jq --raw-output '.SB_USER' $CONFIG_PATH)
echo "SB_USER: ${SB_USER}"

if [[ -z $SB_USER ]]; then 
	echo "No User:Pass Set"
else
	echo "Setting UserName:Password"
	echo "SB_USER: ${SB_USER}"
	export SB_USER="${SB_USER}"
fi

# Save location for SilverBullet data
SB_FOLDER=$(jq --raw-output '.SB_FOLDER' $CONFIG_PATH)
echo "SB_FOLDER: ${SB_FOLDER}"

if [[ -z $SB_FOLDER ]]; then 
	echo "using default SB data folder"
else
	echo "Setting SB data folder"
	echo "SB_FOLDER: ${SB_FOLDER}"
	export SB_FOLDER="${SB_FOLDER}"
	mkdir -p ${SB_FOLDER}
fi

/docker-entrypoint.sh