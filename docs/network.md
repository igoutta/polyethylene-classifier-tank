# Conectar la Pi a una red Wi-Fi

El panel web se abre desde cualquier equipo de la misma red en `http://<ip-de-la-pi>:8080`.

## Raspberry Pi OS Bookworm (NetworkManager)

```sh
sudo nmcli device wifi list
sudo nmcli device wifi connect "MI_SSID" password "MI_CONTRASEÑA"
```

Comprobar la conexión y obtener la IP:

```sh
nmcli connection show --active
hostname -I
```

Para que el panel no cambie de dirección, reservar la IP en el router o usar el nombre `<hostname>.local` (mDNS).

## Versiones anteriores (Bullseye y anteriores, wpa_supplicant)

Cambiar `MI_SSID` y `MI_CONTRASEÑA` por los de la red:

```sh
sudo sh -c 'wpa_passphrase MI_SSID MI_CONTRASEÑA >> /etc/wpa_supplicant/wpa_supplicant.conf'
wpa_cli -i wlan0 reconfigure
```

> Este método no funciona en Bookworm, que ya no usa `wpa_supplicant.conf` para configurar la red.
