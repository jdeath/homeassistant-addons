#!/bin/sh

export TZ=America/Los_Angeles
# Account #1
# No space before/after the = or it will crash

photoLocation=/media/XXX/JohnsPhone
username=me@mail.com
password=SecretPassword
interval=86400
folderstructure={:%Y/%m}

if [ $# -eq 0 ]
  then
    icloudpd --cookie-directory /data --directory $photoLocation -u $username -p $password --watch-with-interval $interval --folder-structure $folderstructure --mfa-provider webui# & <-- if not last account
  else
	icloudpd --cookie-directory /data -u $username -p $password --auth-only
fi
# End Account 1


# Add another copy above for another account
You will have to add a & after each account, except for last one

# Leave this sleep in. This allows time to log into to docker and run authorization
echo "If need to authorize, run this command in home assistant SSH shell (need to disable prodcution mode"
echo "docker exec -it addon_2effc9b9_iclouddownloader /config/iclouddownloader.sh"
sleep 1h
