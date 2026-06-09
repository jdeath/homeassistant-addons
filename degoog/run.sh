#!/bin/sh
set -e

# HA Supervisor connects to ingress_port from config.json.
# nginx listens on that port; degoog runs on a different internal port.
NGINX_PORT="${INGRESS_PORT:-4444}"
DEGOOG_INTERNAL_PORT=4445

# Stamp the port into the nginx config
sed -i "s/%%port%%/${NGINX_PORT}/" /etc/nginx/nginx.conf

# Start nginx in the background (daemon off is set in nginx.conf, & backgrounds it)
nginx &

# Start degoog on the internal port behind nginx
DEGOOG_PORT=${DEGOOG_INTERNAL_PORT} /entrypoint.sh
