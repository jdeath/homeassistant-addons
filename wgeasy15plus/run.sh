#!/bin/sh
set -e

INGRESS_ENTRY=""
if [ -n "${SUPERVISOR_TOKEN}" ]; then
    INGRESS_ENTRY=$(wget -qO- \
        --header="Authorization: Bearer ${SUPERVISOR_TOKEN}" \
        http://supervisor/addons/self/info 2>/dev/null | \
        jq --raw-output '.data.ingress_entry // empty')
fi

if [ -n "${INGRESS_ENTRY}" ]; then
    export NUXT_APP_BASE_URL="${INGRESS_ENTRY}/"

    # Double-quoted heredoc: nginx $vars escaped as \$, shell vars expand normally.
    # Both server blocks use the same rewrite so Nitro always receives the full
    # ingress-prefixed path it was started with.  The direct-access block (51821)
    # additionally strips the token back out of every response so it never reaches
    # the browser, preventing the ingress token from leaking via direct port access.
    cat > /etc/nginx/nginx.conf << EOF
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

    map \$http_upgrade \$connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        listen 8099 default_server;
        location / {
            rewrite ^(.*)\$ ${INGRESS_ENTRY}\$1 break;
            proxy_pass         http://127.0.0.1:51822;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade           \$http_upgrade;
            proxy_set_header   Connection        \$connection_upgrade;
            proxy_set_header   Host              localhost:51822;
            proxy_set_header   X-Real-IP         \$remote_addr;
            proxy_set_header   X-Forwarded-For   \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto https;
            proxy_read_timeout  3600;
            proxy_send_timeout  3600;
        }
    }

    server {
        listen 51821 default_server;
        location / {
            rewrite ^(.*)\$ ${INGRESS_ENTRY}\$1 break;
            proxy_pass         http://127.0.0.1:51822;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade           \$http_upgrade;
            proxy_set_header   Connection        \$connection_upgrade;
            proxy_set_header   Host              localhost:51822;
            proxy_set_header   X-Real-IP         \$remote_addr;
            proxy_set_header   X-Forwarded-For   \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto \$scheme;
            proxy_read_timeout  3600;
            proxy_send_timeout  3600;
            # Disable compression so sub_filter can inspect response bodies.
            proxy_set_header   Accept-Encoding   "";
            # Strip the ingress token from HTML, JS, CSS and JSON responses.
            sub_filter         '${INGRESS_ENTRY}/' '/';
            sub_filter_types   application/javascript text/javascript application/json text/css;
            sub_filter_once    off;
            # Strip the token from Location headers in redirects.
            proxy_redirect     ${INGRESS_ENTRY}/ /;
        }
    }
}
EOF

else
    echo "No ingress entry found, running in direct mode"

    # Single-quoted heredoc: all $ are literal nginx variables.
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
            proxy_pass         http://127.0.0.1:51822;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade           $http_upgrade;
            proxy_set_header   Connection        $connection_upgrade;
            proxy_set_header   Host              localhost:51822;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
            proxy_read_timeout  3600;
            proxy_send_timeout  3600;
        }
    }

    server {
        listen 51821 default_server;
        location / {
            proxy_pass         http://127.0.0.1:51822;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade           $http_upgrade;
            proxy_set_header   Connection        $connection_upgrade;
            proxy_set_header   Host              localhost:51822;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
            proxy_read_timeout  3600;
            proxy_send_timeout  3600;
        }
    }
}
EOF
fi

export PORT=51822
nginx
exec node /app/server/index.mjs
