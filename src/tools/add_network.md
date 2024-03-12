
Change my_SSSID and my_password for your own SSID/Password.

```shell
sudo sh -c 'wpa_passphrase my_SSID my_password >> /etc/wpa_supplicant/wpa_supplicant.conf'
wpa_cli -i wlan0 reconfigure 
```