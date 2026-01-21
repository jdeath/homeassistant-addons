#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
USE_ENV_FILE=false

USE_ENV_FILE=$(grep -o '"USE_ENV_FILE"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_PATH" | tr -d ' "')
USE_ENV_FILE=${USE_ENV_FILE#*:}

echo "USE_ENV_FILE: ${USE_ENV_FILE}"


if [[ "$USE_ENV_FILE" = "true" ]]; then
    
	N8N_ENV_FILES=$(grep -o '"N8N_ENV_FILES"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_PATH" \
  | sed -E 's/.*:[[:space:]]*"?([^"]+)"?.*/\1/'
)

	echo "N8N_ENV_FILES: ${N8N_ENV_FILES}"
	set -a
	source "$N8N_ENV_FILES"
	set +a

fi

cd  /home/node
tini -- /docker-entrypoint.sh
