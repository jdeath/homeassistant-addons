#!/bin/sh
set -e

mkdir -p /share/changedetection
cd /app
python ./changedetection.py -d /share/changedetection