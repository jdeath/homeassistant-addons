#!/bin/sh
set -e

CONFIG_PATH=/data/options.json


cd /config
python3 /app/CruisePriceCheck.py
