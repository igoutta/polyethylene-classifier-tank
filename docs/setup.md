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

## Balanza (HX711)

La balanza usa [hx711-rpi-py](https://pypi.org/project/hx711-rpi-py/), que es un envoltorio de la librería C++ `libhx711`. Hay que compilarla e instalarla **antes** de instalar el proyecto:

```sh
./scripts/install-hx711.sh
```

El script instala las herramientas de compilación y `liblgpio-dev`, compila `libhx711` desde GitHub y la registra con `ldconfig`. Solo hace falta una vez por Pi. El paquete de Python se compila al hacer `uv sync --extra scale` (tarda un poco la primera vez).

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

## Contraseña del panel

Sin contraseña, cualquiera en la red puede encender las bombas. El servicio lee `/etc/polyethylene-tank.env` si existe:

```sh
sudo install -m 600 deploy/polyethylene-tank.env.example /etc/polyethylene-tank.env
sudo nano /etc/polyethylene-tank.env          # cambiar TANK_PASSWORD (y TANK_USER)
sudo systemctl restart polyethylene-classifier-tank
```

El navegador pedirá usuario y contraseña al abrir el panel. Si `TANK_PASSWORD` no está definida, el registro muestra un aviso al arrancar.

## Servos sin vibración: pigpio (opcional)

Con el backend por defecto (lgpio) el PWM de los servos es por software y puede vibrar. En la Pi 4, pigpio genera el PWM por hardware (DMA). No funciona en la Pi 5.

```sh
sudo apt install -y pigpio
sudo systemctl daemon-reload
sudo systemctl enable --now pigpiod
systemctl status pigpiod                       # debe estar "active (running)"
```

Luego descomentar `GPIOZERO_PIN_FACTORY=pigpio` en `/etc/polyethylene-tank.env` y reiniciar el servicio del tanque. Para volver a lgpio, comentar la línea. *(Por verificar en la Pi: que los servos dejen de vibrar.)*

## Archivos que escribe

| Qué | Dónde | Variable para cambiarlo |
|---|---|---|
| Tiempos fijados desde el panel | `~/.local/state/polyethylene-tank/tiempos.json` | `TANK_STATE_DIR` |
| Último peso de la balanza | `/dev/shm/polyethylene-tank/peso.json` (en RAM) | `TANK_LIVE_DIR` |

Para volver a los tiempos de `config.py`, borrar `tiempos.json` y reiniciar el servicio.

## Siguientes pasos

- Pines, conexiones y calibración de la balanza: [hardware.md](hardware.md)
- Conectar la Pi a la red Wi-Fi: [network.md](network.md)
- Si algo no funciona: [troubleshooting.md](troubleshooting.md)
