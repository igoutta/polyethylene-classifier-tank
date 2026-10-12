# Problemas frecuentes

Estos puntos vienen de la revisión del código y de cómo funcionan el HX711 y gpiozero; no todos se han comprobado en la Pi real. Marcados con *(por verificar)* los que dependen del hardware.

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

- **La pantalla no muestra nada:** comprobar `i2cdetect -y 1` (debe aparecer `27`), que I2C esté activo en `raspi-config` y el cableado SDA/SCL. Algunas pantallas usan la dirección `0x3F`.
- **`TimeoutError: HX711 sin datos`:** el chip no responde. Revisar alimentación, que `DT` y `SCK` estén en los pines BCM 9 y 11 y que no estén cruzados.
- **`TimeoutError: ... lecturas inválidas`:** todas las lecturas se descartaron. Causas posibles: cable suelto (DOUT siempre en alto) o que el sistema esté muy cargado y los pulsos de reloj duren más de 50 µs. Cerrar otros procesos, usar cables cortos o pasar a la balanza Arduino.
- **El peso salta o es ruidoso:** el driver ya usa la mediana de varias lecturas. Revisar la alimentación del HX711 y que la celda de carga esté bien sujeta.
- **El peso sale con signo invertido:** cambiar el signo de `SCALE_REFERENCE_UNIT`.

## Conflicto entre el motor NEMA y la LCD

El motor usa `J8:3` y `J8:5`, que son los pines I2C de la pantalla. Si la LCD y el motor están en la misma Pi puede dejar de verse la pantalla, o el motor moverse al leer la LCD. Solución: mover el motor a otros pines (cambiar `NEMA_STEP` y `NEMA_DIR` en `config.py`) o poner la balanza en una Pi/Arduino aparte.
