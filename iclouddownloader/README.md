# Home assistant add-on: iCloud Downloader

1. Install Addon
1. Run Addon, it will fail, but will create the directory we need for the next step
1. Copy iclouddownloader.sh from this repo into /addon_configs/2effc9b9_iclouddownloader
1. Edit the command with your username,password, and location you want to download files
1. You should be able to run multiple lines in the code use multiple accounts
1. Review all the possible commands here and setup as you like: https://pypi.org/project/icloudpd/1.12.0/
1. You can mount an smb/nfs share in Home Assistant Settings->System->Storage to the media directory and point to that location. Location will be /media/ShareName/ with any directory structure under that you wish, where sharename is what you named the share in homeassistant
1. Run Addon, it will fail (do not hit stop on the addon)
1. In next hour, log into home assistant via SSH (you must set protection mode to false in ssh addon)
1. run 'docker exec -it addon_2effc9b9_iclouddownloader /config/iclouddownloader.sh authorize'
1. Enter the 2fa code that shows on your iPhone (you will need to repeat this step every 2 months)
1. Hit Control-C or exit out of terminal
1. Restart addon and it should start downloading photos





[repository]: https://github.com/jdeath/homeassistant-addons
