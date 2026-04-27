#!/bin/sh
set -e

mkdir -p /share/changedetection

# HA supervisor injects INGRESS_PORT; fall back to the config.json default
NGINX_PORT="${INGRESS_PORT:-5000}"

# Stamp the port into the nginx config
sed -i "s/%%port%%/${NGINX_PORT}/" /etc/nginx/nginx.conf

# Start nginx in the background
nginx &

# Start changedetection on the internal port
cd /app
python ./changedetection.py -d /share/changedetection -p 5001
