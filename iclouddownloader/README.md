# Home assistant add-on: iCloud Downloader

1. Install Addon
1. Run Addon, it will fail, but will create the directory we need for the next step
1. Copy iclouddownloader.sh from this repo into /addon_configs/2effc9b9_iclouddownloader
1. Edit the command with your username,password, and location you want to download files
1. You should be able to add multiple accounts by copying the account block, but get 1 account working first! All but the last account should have a & ending the line, or the addon will quit after 1 hour
1. Review all the possible commands here and setup as you like: https://pypi.org/project/icloudpd/1.12.0/
1. You can mount an smb/nfs share in Home Assistant Settings->System->Storage to the media directory and point to that location. Location will be /media/ShareName/ with any directory structure under that you wish, where sharename is what you named the share in homeassistant
1. Run/restart the Addon, it will fail again. (Do not hit stop on the addon)
1. In next hour, log into home assistant via SSH (you must set protection mode to false in ssh addon)
1. run 'docker exec -it addon_2effc9b9_iclouddownloader /config/iclouddownloader.sh authorize'
1. Enter the 2fa code that shows on your iPhone (you will need to repeat this reauthentication step every 2 months)
1. Hit Control-C or exit out of terminal
1. Restart addon one last time and it should start downloading photos.





[repository]: https://github.com/jdeath/homeassistant-addons
