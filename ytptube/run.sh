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

YTP_CONSOLE_ENABLED=false
YTP_CONSOLE_ENABLED=$(jq --raw-output '.YTP_CONSOLE_ENABLED' $CONFIG_PATH)
echo "YTP_CONSOLE_ENABLED: ${YTP_CONSOLE_ENABLED}"
export YTP_CONSOLE_ENABLED="${YTP_CONSOLE_ENABLED}"

YTP_BROWSER_ENABLED=false
YTP_BROWSER_ENABLED=$(jq --raw-output '.YTP_BROWSER_ENABLED' $CONFIG_PATH)
echo "YTP_BROWSER_ENABLED: ${YTP_BROWSER_ENABLED}"
export YTP_BROWSER_ENABLED="${YTP_BROWSER_ENABLED}"

# Fetch ingress entry from Supervisor API
INGRESS_ENTRY=""
if [ -n "${SUPERVISOR_TOKEN}" ]; then
    INGRESS_ENTRY=$(curl -s \
        -H "X-Supervisor-Token: ${SUPERVISOR_TOKEN}" \
        http://supervisor/addons/self/info \
        | jq --raw-output '.data.ingress_entry // empty')
fi

if [ -n "${INGRESS_ENTRY}" ]; then
    echo "YTP_BASE_PATH: ${INGRESS_ENTRY}"
    export YTP_BASE_PATH="${INGRESS_ENTRY}"
fi

# Generate nginx config with ingress entry baked into the direct-access server block
export INGRESS_ENTRY
envsubst '${INGRESS_ENTRY}' < /etc/nginx/nginx.conf.tmpl > /etc/nginx/nginx.conf

# Start nginx reverse proxy (ingress 8099 + direct 8082 → app 8081)
nginx

/opt/python/bin/python /app/app/main.py --ytp-process
