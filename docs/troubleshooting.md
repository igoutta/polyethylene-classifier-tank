# Problemas frecuentes

Estos puntos vienen de la revisión del código y de la documentación de las librerías; no todos se han comprobado en la Pi real. Marcados con *(por verificar)* los que dependen del hardware.

## El panel no abre

- Comprobar que el servicio corre: `systemctl status polyethylene-classifier-tank` y `journalctl -u polyethylene-classifier-tank -f`.
- Abrir `http://<ip-de-la-pi>:8080` desde un equipo de la **misma red**. La IP: `hostname -I`.
- `Address already in use`: otro proceso usa el puerto 8080 (¿el servicio y una ejecución manual al mismo tiempo?). Cambiar `PORT` en `config.py` o detener el otro.
- El panel debe correr con un **solo proceso**; no usar `--workers` con uvicorn, porque cada proceso intentaría tomar los pines.

## Error al iniciar: pines o `lgpio`

- `lgpio` no instalado: usar `uv run --extra pi ...` (o `uv sync --extra pi`). Si falla la compilación: `sudo apt install liblgpio-dev swig`.
- `GPIO busy` / pin ocupado: otro programa (o una ejecución anterior que no cerró) tiene el pin. Detener el servicio antes de correr un script de `tools/`.
- Permisos: el usuario debe estar en el grupo `gpio` (`sudo usermod -aG gpio $USER`, volver a iniciar sesión).
- Para probar sin hardware: `GPIOZERO_PIN_FACTORY=mock GPIOZERO_MOCK_PIN_CLASS=mockpwmpin`.

## El ciclo no avanza o se comporta raro

- **Se queda "Llenando el tanque" 15 s y sigue de largo:** el fin de carrera no detectó el tanque lleno. Se imprime `AVISO: el sensor no detectó...` en el registro. Revisar el cableado y que el sensor sea activo en alto.
- **El sensor responde con retraso** *(por verificar)*: en `tank.py` el sensor se crea con `bounce_time=5`, que gpiozero interpreta en **segundos**. Probablemente se quiso `0.005`.
- **Los servos vibran o se mueven solos** *(por verificar)*: es el PWM por software de gpiozero. En una Pi 4 o anterior se puede usar pigpio (`sudo apt install pigpio`, `sudo systemctl enable --now pigpiod` y `GPIOZERO_PIN_FACTORY=pigpio`), pero **pigpio no funciona en la Pi 5**; allí la opción es PWM por hardware del sistema operativo (GPIO 12 y 13 son pines de PWM por hardware) o un controlador de servos externo (por ejemplo PCA9685 por I2C).
- **PARAR tarda unos segundos:** es normal. Detener la etapa es inmediato, pero luego se mueven los servos a su posición de reposo (~5 s).

## La balanza

- **`uv sync --extra scale` falla al compilar `hx711-rpi-py`:** falta `libhx711` o las herramientas de compilación. Ejecutar `./scripts/install-hx711.sh` y volver a intentar. Los únicos binarios ya compilados que publica el paquete son para Python 3.11 en ARM de 32 bits; en otro caso (Pi OS de 64 bits u otra versión de Python) se compila desde el código fuente, lo que necesita el script.
- **`error while loading shared libraries: libhx711.so`:** la librería no está registrada: `sudo ldconfig` y comprobar con `ldconfig -p | grep hx711`.
- **La pantalla no muestra nada:** comprobar `i2cdetect -y 1` (debe aparecer `27`), que I2C esté activo en `raspi-config` y el cableado SDA/SCL. Algunas pantallas usan la dirección `0x3F`.
- **`GpioException` o `TimeoutException` al iniciar:** el HX711 no responde. Revisar alimentación, que `DT` y `SCK` estén en los pines BCM 9 y 11 y que no estén cruzados, y que no haya otro proceso usando esos pines.
- **El peso salta o es ruidoso:** el servicio ya usa la mediana de todas las muestras de cada segundo. Revisar la alimentación del HX711 y que la celda esté bien sujeta. La librería hace un mejor trabajo con prioridad de tiempo real, que solo se obtiene con privilegios (la documentación de `libhx711` indica ejecutarla con `sudo`) *(por verificar en el servicio de systemd)*. Si sigue ruidoso, la balanza en Arduino de `firmware/scale_arduino/` evita el problema porque un microcontrolador tiene tiempos exactos.
- **El peso sale con signo invertido o con un factor equivocado:** recalibrar (ver [hardware.md](hardware.md)).

## Conflicto entre el motor NEMA y la LCD

El motor usa `J8:3` y `J8:5`, que son los pines I2C de la pantalla. Si la LCD y el motor están en la misma Pi puede dejar de verse la pantalla, o el motor moverse al leer la LCD. Solución: mover el motor a otros pines (cambiar `NEMA_STEP` y `NEMA_DIR` en `config.py`) o poner la balanza en una Pi/Arduino aparte.
