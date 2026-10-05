#!/bin/bash
set -e

cd /app/data

rmdir /app/public/uploads
mkdir -p /app/data/uploads
ln -s /app/data/uploads /app/public/uploads

rmdir /app/public/generated
mkdir -p /app/data/generated
ln -s /app/data/generated /app/public/generated

rmdir  /app/public/generated-audio
mkdir -p /app/data/generated-audio
ln -s /app/data/generated-audio /app/public/generated-audio

[ -d /root/odm-backups ] && rmdir /root/odm-backups
mkdir -p /app/data/backups
ln -s /app/data/backups /root/odm-backups

set -a
source /app/data/env.server
set +a

node /app/server.js