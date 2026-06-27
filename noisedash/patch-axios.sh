#!/bin/sh
# Patch compiled JS bundle for ingress support:
# 1. Set axios baseURL dynamically from location.pathname
# 2. Set Vue Router base dynamically from location.pathname
# 3. Set webpack publicPath dynamically so lazy-loaded chunks load through ingress

for jsfile in /var/noisedash/dist/js/app.*.js; do
    if [ -f "$jsfile" ]; then
        PATCH_FILE="$jsfile" python3 << 'PYEOF'
import os
jsfile = os.environ["PATCH_FILE"]
with open(jsfile, 'r') as f:
    content = f.read()

# Runtime function to extract ingress prefix from pathname
base_fn = r'''(function(){var p=location.pathname;var m=p.match(/^\/api\/[^\/]+\/[^\/]+\/?/);return m?m[0].replace(/\/$/,""):""})()'''

# 1. Patch axios: inject baseURL into create() config
content = content.replace('withCredentials:!0', 'withCredentials:!0,baseURL:'+ base_fn)
content = content.replace('withCredentials:true', 'withCredentials:true,baseURL:'+ base_fn)

# 2. Patch Vue Router: replace base:"/" with dynamic base
content = content.replace('base:"/"', 'base:'+ base_fn)

# 3. Patch webpack publicPath: replace .p="/" with dynamic value
# This ensures lazy-loaded route chunks (login, register, admin, account)
# are fetched through the ingress proxy instead of bypassing it
content = content.replace('.p="/"', '.p='+ base_fn + '+"/"', 1)

with open(jsfile, 'w') as f:
    f.write(content)
PYEOF
    fi
done
