#!/bin/sh
set -e

mkdir -p /share/minecraftbe
cd /share/minecraftbe/
/usr/local/bin/entrypoint-demoter --match /share/minecraftbe --debug --stdin-on-term stop /opt/bedrock-entry.sh
