#!/bin/sh
set -e
sed -i 's/127.0.0.1/0.0.0.0/g' /config/configs.toml || true
cd /config
/bin/readeck serve
