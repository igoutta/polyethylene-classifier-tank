# Instalación en la Raspberry Pi

## Dependencias del sistema

```sh
sudo apt update && sudo apt upgrade
sudo apt install -y i2c-tools python3-smbus liblgpio-dev
```

Activar I2C (para la pantalla LCD): `sudo raspi-config` → *Interface Options* → *I2C* → *Yes*, y reiniciar. Comprobar que la pantalla responde en la dirección `0x27`:

```sh
lsmod | grep i2c_
i2cdetect -y 1
```

> Los pines `J8:3` y `J8:5` (motor NEMA) son los de I2C (SDA/SCL). Si el motor y la LCD están en la misma Pi hay un conflicto: ver [hardware.md](hardware.md).

## Proyecto

```sh
git clone <repositorio> ~/polyethylene-classifier-tank
cd ~/polyethylene-classifier-tank
uv sync --extra pi --extra scale
```

## Iniciar automáticamente (systemd)

```sh
sudo cp deploy/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now polyethylene-classifier-tank polyethylene-scale
journalctl -u polyethylene-classifier-tank -f   # ver el registro
```

Los servicios asumen el usuario `ga`, el repositorio en `/home/ga/polyethylene-classifier-tank` y uv en `/home/ga/.local/bin/uv`; ajustar en los `.service` si es distinto.

## Siguientes pasos

- Pines, conexiones y calibración de la balanza: [hardware.md](hardware.md)
- Conectar la Pi a la red Wi-Fi: [network.md](network.md)
- Si algo no funciona: [troubleshooting.md](troubleshooting.md)
