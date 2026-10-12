# Hardware y conexiones

Los pines se nombran en la numeración física de la Raspberry Pi (`J8:<n>`, de 1 a 40). Todos están definidos en [`config.py`](../src/polyethylene_tank/config.py); si algo se recablea, solo hay que cambiarlo ahí.

## Tanque

| Función | Pin | GPIO (BCM) | Tipo | Notas |
|---|---|---|---|---|
| Fin de carrera (tanque lleno) | `J8:19` | 10 | Entrada | Activo en alto (pull-down) |
| Relé bomba de llenado | `J8:7` | 4 | Salida | Activo en alto |
| Relé bomba de corriente | `J8:11` | 17 | Salida | Activo en alto |
| Motor NEMA, *enable* (STEP, velocidad) | `J8:13` | 27 | PWM | Antes en `J8:3` |
| Motor NEMA, *phase* (DIR, dirección) | `J8:15` | 22 | Salida | Antes en `J8:5` |
| Servo `sapo` (desfogue) | `J8:33` | 13 | PWM | Abre/cierra el tubo de escape |
| Servo `túnel` (limpieza del tubo) | `J8:32` | 12 | PWM | Barre el tubo con tiempos fijos |
| Botón iniciar | `J8:37` | 26 | Entrada | Entre el pin y GND (pull-up interno) |
| Botón parar | `J8:35` | 19 | Entrada | Parada de emergencia; entre el pin y GND |

- **Fin de carrera:** antirrebote de 5 ms (`FIN_CARRERA_BOUNCE_SEC`). Antes era `5`, que gpiozero interpreta como cinco **segundos**.
- **Botones:** antirrebote de 50 ms. PARAR corta bombas y motor al instante y no depende del panel ni de la red. Si un botón no está conectado, el pull-up interno lo deja en reposo y no hace nada.

### Motor NEMA: pines cambiados

El motor estaba en `J8:3` y `J8:5`, que son SDA y SCL de I2C (con resistencias pull-up fijas) y los comparte la pantalla LCD de la balanza. Ahora está en `J8:13` (STEP) y `J8:15` (DIR), pines sin otra función, junto al relé de `J8:11`. **Hay que mover los dos cables** en la Pi: STEP del pin físico 3 al 13 y DIR del 5 al 15. La tierra del driver puede ir a `J8:9` o `J8:14`.

`J8:3` y `J8:5` quedan solo para la LCD.

### Servos

- El `sapo` es un servo de posición: `max()` abre el tubo de escape y `min()` lo cierra.
- El `túnel` parece de rotación continua *(inferido, por verificar)*: el código hace `min()` 1,7 s y `max()` 0,95 s con esperas fijas para barrer el tubo (`Tank._limpiar_tubo`), lo que solo tiene sentido si el servo gira según el tiempo y no según una posición.
- Se llama a `detach()` después de mover cada servo para que dejen de recibir señal PWM y no vibren ni se muevan solos.
- El PWM es por software con el backend por defecto de gpiozero (lgpio) y puede vibrar. En la Pi 4 se puede usar pigpio, con PWM temporizado por hardware, sin cambiar el código: ver [setup.md](setup.md#servos-sin-vibración-pigpio-opcional).

## Balanza

| Función | Pin | GPIO (BCM) |
|---|---|---|
| HX711 `DT` (datos) | `J8:21` | 9 |
| HX711 `SCK` (reloj) | `J8:23` | 11 |
| LCD I2C `SDA` | `J8:3` | 2 |
| LCD I2C `SCL` | `J8:5` | 3 |

- Los pines del HX711 se dan en numeración **BCM** (`SCALE_DATA`, `SCALE_CLOCK` en `config.py`), no en la `J8` del resto.
- La LCD es de 16×2 con adaptador PCF8574 en la dirección `0x27`.
- Alimentar el HX711 a 3,3 V si se comunica directo con la Pi (los GPIO no toleran 5 V).

### Balanza alternativa en Arduino

[`firmware/scale_arduino/code.ino`](../firmware/scale_arduino/code.ino) hace lo mismo en un Arduino (HX711 en pines 3 y 5, LCD I2C en `0x27`, factor de calibración 696). Un microcontrolador tiene tiempos de reloj exactos, así que es la opción más robusta si el driver en Python da lecturas ruidosas. Necesita las librerías `LCD-I2C` y `HX711_ADC`.

## Calibración de la balanza

El servicio hace el cero con la báscula vacía al arrancar (tarda ~10 s), así que solo hay que calibrar la unidad de referencia (`SCALE_REFERENCE_UNIT` en `config.py`, cuentas por gramo):

1. Detener el servicio de la balanza para liberar los pines: `sudo systemctl stop polyethylene-scale`.
2. Ejecutar el script de calibración de hx711-rpi-py con los pines BCM de datos y reloj, y seguir las instrucciones (pide la unidad, el peso conocido y que se quite y se ponga el objeto):

   ```sh
   curl -O https://raw.githubusercontent.com/endail/hx711-rpi-py/master/src/calibrate.py
   uv run --extra scale python calibrate.py 9 11
   ```

3. Copiar el valor `REFERENCE UNIT` que imprime a `SCALE_REFERENCE_UNIT` y reiniciar el servicio.

Si el signo del peso sale invertido, el script ya lo refleja en el signo de la unidad de referencia.
