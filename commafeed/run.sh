#!/bin/bash
set -e

CONFIG_PATH=/data/options.json
USE_ENV_FILE=false
USE_ENV_FILE=$(jq --raw-output '.USE_ENV_FILE' $CONFIG_PATH)
echo "USE_ENV_FILE: ${USE_ENV_FILE}"

ls

if [[ "$USE_ENV_FILE" = "true" ]]; then
    
	N8N_ENV_FILES=$(jq --raw-output '.N8N_ENV_FILES' $CONFIG_PATH)
	echo "N8N_ENV_FILES: ${N8N_ENV_FILES}"
	set -a
	source "$N8N_ENV_FILES"
	set +a
	#cp "$N8N_ENV_FILES" /commafeed/
fi

cd /commafeed/
./commafeed


