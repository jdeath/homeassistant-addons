#!/bin/sh


python /mcp_server.py --http &

sleep 5
chown searxng:searxng /etc/searxng/ods_config.json

set_url=$(cat /data/options.json | grep set_base_url_for_ingress | cut -d: -f2 | xargs)

if [ "$set_url" = "true" ]; then
export SEARXNG_BASE_URL

header="Authorization: Bearer $SUPERVISOR_TOKEN"

SEARXNG_BASE_URL=$(wget -qO- --header="$header" \
    "http://supervisor/addons/self/info" \
    | sed -n 's/.*"ingress_url":"\([^"]*\)".*/\1/p') #sed by ai
fi

if [ ! -f /etc/searxng/custom.sh ]; then
    cp /custom.sh /etc/searxng/custom.sh
fi

chmod +x /etc/searxng/custom.sh

exec /etc/searxng/custom.sh
