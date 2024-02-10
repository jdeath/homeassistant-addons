#!/bin/sh
set -e


CONFIG_PATH=/data/options.json
cat /data/options.json
DELETE_FILE_ON_TRASHCAN=false
DELETE_FILE_ON_TRASHCAN=$(jq --raw-output '.DELETE_FILE_ON_TRASHCAN' $CONFIG_PATH)
echo "DELETE_FILE_ON_TRASHCAN: ${DELETE_FILE_ON_TRASHCAN}"
export DELETE_FILE_ON_TRASHCAN="${DELETE_FILE_ON_TRASHCAN}"

ls
pwd
./docker-entrypoint.sh