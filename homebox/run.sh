#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

ENV_KEYS="
HBOX_OPTIONS_ALLOW_REGISTRATION
HBOX_AUTH_API_KEY_PEPPER
HBOX_OIDC_ENABLED
HBOX_OIDC_ISSUER_URL
HBOX_OIDC_CLIENT_ID
HBOX_OIDC_CLIENT_SECRET
"

for key in $ENV_KEYS; do
	value=$(jq --raw-output --arg key "$key" '.[$key] // empty' "$CONFIG_PATH")
	case "$key" in
        # Redact sensitive values in logs
		HBOX_AUTH_API_KEY_PEPPER|HBOX_OIDC_CLIENT_SECRET)
			if [ -n "$value" ]; then
				echo "$key: [REDACTED]"
			else
				echo "$key: [empty]"
			fi
			;;
		*)
			echo "$key: ${value}"
			;;
	esac

	export "$key=$value"
done

# Start nginx for ingress (listens on 8099, proxies to app on 7745)
NGINX_PORT="${INGRESS_PORT:-8099}"
sed -i "s/%%port%%/${NGINX_PORT}/" /etc/nginx/nginx.conf
nginx &

# Start the app on internal port 7745
/app/api
