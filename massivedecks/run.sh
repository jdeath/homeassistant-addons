#!/bin/sh
set -e
cd /

ls
cd /massivedecks-2.6.0/server/
nginx
node --es-module-specifier-resolution=node dist/index.js


