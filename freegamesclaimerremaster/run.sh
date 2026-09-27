#!/bin/bash
set -e
CONFIG_PATH=/data/options.json
set -a
source "/fgc/data/config.env"
set +a
python3 main.py


