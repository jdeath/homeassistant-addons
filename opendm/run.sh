#!/bin/bash
set -e

cd /config

#rmdir /app/data
mkdir -p /config/data
ln -s /config/data /app/data

#rm /app/public/uploads
mkdir -p /config/uploads
ln -s /config/uploads /app/public/uploads

#rm /app/public/generated
mkdir -p /config/generated
ln -s /config/generated /app/public/generated

#rm  /app/public/generated-audio
mkdir -p /config/generated-audio
ln -s /config/generated-audio /app/public/generated-audio

#rm /root/odm-backups
mkdir -p /config/backups
ln -s /config/backups /root/odm-backups

set -a
source /config/env.server
set +a

node /app/server.js