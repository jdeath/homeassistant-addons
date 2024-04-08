#!/bin/sh

# Account #1
# No space before/after the = or it will crash

photoLocation=/media/XXX/JohnsPhone
username=me@mail.com
password=SecretPassword
interval=86400
folderstructure={:%Y/%m}

icloudpd --cookie-directory /data --directory $photoLocation -u $username -p $password --watch-with-interval $interval --folder-structure $folderstructure &


# Add another copy above for another account

# Leave this sleep in. This allows time to log into to docker and run authorization
echo "If need to authorize, run this command in home assistant SSH shell (need to disable prodcution mode"
echo "docker exec -it addon_2effc9b9_iclouddownloader /config/iclouddownloader.sh"
sleep 1h
