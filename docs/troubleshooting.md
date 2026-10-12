# Problemas frecuentes

Estos puntos vienen de la revisión del código y de la documentación de las librerías; no todos se han comprobado en la Pi real. Marcados con *(por verificar)* los que dependen del hardware.

## El panel no abre

- Comprobar que el servicio corre: `systemctl status polyethylene-classifier-tank` y `journalctl -u polyethylene-classifier-tank -f`.
- Abrir `http://<ip-de-la-pi>:8080` desde un equipo de la **misma red**. La IP: `hostname -I`.
- **El navegador pide contraseña:** está definida `TANK_PASSWORD` en `/etc/polyethylene-tank.env`; usar ese usuario y contraseña.
- `Address already in use`: otro proceso usa el puerto 8080 (¿el servicio y una ejecución manual al mismo tiempo?). Cambiar `PORT` en `config.py` o detener el otro.
- El panel debe correr con un **solo proceso**; no usar `--workers` con uvicorn, porque cada proceso intentaría tomar los pines.

## Error al iniciar: pines o `lgpio`

- `lgpio` no instalado: usar `uv run --extra pi ...` (o `uv sync --extra pi`). Si falla la compilación: `sudo apt install liblgpio-dev swig`.
- `GPIO busy` / pin ocupado: otro programa (o una ejecución anterior que no cerró) tiene el pin. Detener el servicio antes de correr un script de `tools/`.
- Permisos: el usuario debe estar en el grupo `gpio` (`sudo usermod -aG gpio $USER`, volver a iniciar sesión).
- Para probar sin hardware: `GPIOZERO_PIN_FACTORY=mock GPIOZERO_MOCK_PIN_CLASS=mockpwmpin`.

## El ciclo no avanza o se comporta raro

- **Error "El tanque no se llenó en 15 s":** el fin de carrera no detectó el tanque lleno a tiempo, así que se apagó todo. Revisar el sensor (cableado, que sea activo en alto) y la bomba de llenado. Si el tanque tarda más en llenarse, subir el *llenado máximo* en el panel. Se vuelve a intentar con COMENZAR.
- **Otro error en el panel:** el ciclo se detuvo por una excepción inesperada. El detalle completo está en `journalctl -u polyethylene-classifier-tank`.
- **Los servos vibran o se mueven solos** *(por verificar)*: es el PWM por software. En la Pi 4, activar pigpio (ver [setup.md](setup.md#servos-sin-vibración-pigpio-opcional)).
- **El servicio no arranca tras activar pigpio:** `pigpiod` no está corriendo (`systemctl status pigpiod`). Activarlo o comentar `GPIOZERO_PIN_FACTORY=pigpio` en `/etc/polyethylene-tank.env`.
- **PARAR tarda unos segundos:** es normal. Bombas y motor se apagan al instante; luego los servos vuelven a su posición de reposo (~5 s).
- **Un botón físico no responde:** debe ir entre su pin y GND. Con `journalctl -u polyethylene-classifier-tank -f` se ve `Botón INICIAR presionado` o `Botón PARAR presionado` al pulsarlo.
- **Los tiempos del panel no se guardan:** revisar permisos de `~/.local/state/polyethylene-tank/`. Si `tiempos.json` no es válido, el registro lo avisa y se usan los de `config.py`.

## La balanza

- **`uv sync --extra scale` falla al compilar `hx711-rpi-py`:** falta `libhx711` o las herramientas de compilación. Ejecutar `./scripts/install-hx711.sh` y volver a intentar. Los únicos binarios ya compilados que publica el paquete son para Python 3.11 en ARM de 32 bits; en otro caso (Pi OS de 64 bits u otra versión de Python) se compila desde el código fuente, lo que necesita el script.
- **`error while loading shared libraries: libhx711.so`:** la librería no está registrada: `sudo ldconfig` y comprobar con `ldconfig -p | grep hx711`.
- **La pantalla no muestra nada:** comprobar `i2cdetect -y 1` (debe aparecer `27`), que I2C esté activo en `raspi-config` y el cableado SDA/SCL. Algunas pantallas usan la dirección `0x3F`.
- **`GpioException` o `TimeoutException` al iniciar:** el HX711 no responde. Revisar alimentación, que `DT` y `SCK` estén en los pines BCM 9 y 11 y que no estén cruzados, y que no haya otro proceso usando esos pines.
- **El panel dice "Balanza: sin datos":** el servicio de la balanza no está corriendo o no publicó en los últimos 5 s (`systemctl status polyethylene-scale`).
- **El peso salta o es ruidoso:** el servicio ya usa la mediana de todas las muestras de cada segundo. Revisar la alimentación del HX711 y que la celda esté bien sujeta. La librería hace un mejor trabajo con prioridad de tiempo real, que solo se obtiene con privilegios (la documentación de `libhx711` indica ejecutarla con `sudo`) *(por verificar en el servicio de systemd)*. Si sigue ruidoso, la balanza en Arduino de `firmware/scale_arduino/` evita el problema porque un microcontrolador tiene tiempos exactos.
- **El peso sale con signo invertido o con un factor equivocado:** recalibrar (ver [hardware.md](hardware.md)).

## El motor NEMA no se mueve

Si el software está actualizado pero los cables no: el motor ahora se controla desde `J8:13` (STEP) y `J8:15` (DIR), no desde `J8:3` y `J8:5`. Mover los cables (ver [hardware.md](hardware.md)). Para probarlo solo, con el servicio detenido: `uv run --extra pi python tools/try_nema.py`.
