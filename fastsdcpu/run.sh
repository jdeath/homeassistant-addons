#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

MODE=$(jq --raw-output '.MODE' $CONFIG_PATH)
echo "MODE: ${MODE}"
export MODE="${MODE}"

DEVICE=$(jq --raw-output '.DEVICE' $CONFIG_PATH)
echo "DEVICE: ${DEVICE}"
export DEVICE="${DEVICE}"

NGINX_PORT="${INGRESS_PORT:-8099}"

# Stamp the ingress port into the nginx config
sed -i "s/%%port%%/${NGINX_PORT}/" /etc/nginx/nginx.conf

# Force Output Path To /config/results mapped to /addon-configs/2effc9b9_fastsdcpu/results
sed -i 's|join_paths(get_app_path(), constants\.RESULTS_DIRECTORY)|"/config/results/"|g' /app/src/paths.py

# Do not change settings, because the do not persist anyways
# Force settings Path To /config/results mapped to /addon-configs/2effc9b9_fastsdcpu/results
#sed -i 's|join_paths(get_app_path(), constants\.CONFIG_DIRECTORY)|"/config/configs/"|g' /app/src/paths.py

# Copy default settings if they do not exist
#cp -n /app/configs/* /config/configs/

# Start nginx in the background (ingress on $NGINX_PORT, app on 7860)
nginx &

cd /config

case "$MODE" in
  api)
    python3 -u /app/src/app.py --api --port 7860
    ;;
  mcp)
    python3 -u /app/src/app.py --mcp --port 7860
    ;;
  *)
    python3 -u /app/src/app.py --webui
    ;;
esac
