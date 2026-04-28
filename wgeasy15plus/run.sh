#!/bin/sh
set -e

# Get the ingress entry path (e.g. /api/hassio_ingress/abc123) from the
# Supervisor API so nginx and Nuxt use the same base path.
INGRESS_ENTRY=""
if [ -n "${SUPERVISOR_TOKEN}" ]; then
    INGRESS_ENTRY=$(wget -qO- \
        --header="Authorization: Bearer ${SUPERVISOR_TOKEN}" \
        http://supervisor/addons/self/info 2>/dev/null | \
        jq --raw-output '.data.ingress_entry // empty')
fi

if [ -n "${INGRESS_ENTRY}" ]; then
    #echo "Ingress entry: ${INGRESS_ENTRY}"
    # Tell Nuxt 3 / Nitro its base URL so client-side routing and asset
    # paths are generated correctly for the HA ingress sub-path.
    export NUXT_APP_BASE_URL="${INGRESS_ENTRY}/"
    REWRITE_RULE="rewrite ^(.*)$ ${INGRESS_ENTRY}\$1 break;"
else
    echo "No ingress entry found, running in direct mode"
    REWRITE_RULE=""
fi

# Generate nginx.conf at runtime so we can embed the ingress path.
# Single-quoted heredoc keeps nginx $variables literal; only REWRITE_RULE
# (a shell variable) is substituted via sed afterwards.
cat > /etc/nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /dev/stderr warn;
pid /var/run/nginx.pid;

events { worker_connections 1024; }

http {
    include      /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile     on;
    keepalive_timeout 65;

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        listen 8099 default_server;
        location / {
            __REWRITE_RULE__
            proxy_pass         http://127.0.0.1:51821;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade           $http_upgrade;
            proxy_set_header   Connection        $connection_upgrade;
            proxy_set_header   Host              localhost:51821;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto https;
            proxy_read_timeout  3600;
            proxy_send_timeout  3600;
        }
    }
}
EOF

sed -i "s|__REWRITE_RULE__|${REWRITE_RULE}|" /etc/nginx/nginx.conf

export PORT=51821
nginx
exec node /app/server/index.mjs
