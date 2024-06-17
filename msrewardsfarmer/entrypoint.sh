#!/bin/sh

# clean up old runtime files
echo "$(date +"%Y-%m-%d %H:%M:%S,%3N") [INFO] Cleaning up tmp folder"
rm -rf /tmp/* /tmp/.*

# start virtual display
Xvfb $DISPLAY -screen 1 1280x800x8 -nolisten tcp &

# start the bot
echo "$(date +"%Y-%m-%d %H:%M:%S,%3N") [INFO] Starting bot"
exec $@ $PARAMS
