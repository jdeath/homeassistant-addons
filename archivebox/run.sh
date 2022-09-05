#!/bin/sh
set -e

mkdir -p /data/archivebox
cd /data/archivebox
archivebox server --quick-init 0.0.0.0:8000