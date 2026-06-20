#!/bin/sh
set -e

# nginx listens on ingress_port; app runs on a different internal port
NGINX_PORT="${INGRESS_PORT:-8099}"
APP_INTERNAL_PORT=11325

# Stamp the port into the nginx config
sed -i "s/%%port%%/${NGINX_PORT}/" /etc/nginx/nginx.conf

# Start nginx in the background (daemon off is set in nginx.conf, & backgrounds it)
nginx &

# Start the Bedrock Server Manager app on the internal port behind nginx
exec bedrock-server-manager web start --host 0.0.0.0 --port "$APP_INTERNAL_PORT"
