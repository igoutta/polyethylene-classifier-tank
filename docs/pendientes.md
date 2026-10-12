# Pendientes

Mejoras y comprobaciones que quedan por hacer, de más a menos importante. Al resolver una, borrarla de aquí (o moverla a *Hecho* con el commit).

## 1. Relé de la bomba de llenado durante el arranque (seguridad)

**Problema.** El relé de la bomba de llenado está en `J8:7` (GPIO4). En la Pi 4, los GPIO 0 a 8 tienen *pull-up* débil por defecto, así que mientras la Pi arranca (antes de que el servicio tome el pin) y posiblemente cuando el servicio se detiene, ese pin queda ligeramente en alto. Con un módulo de relé activo en alto, **la bomba podría encenderse sola** en esos momentos. El relé de la bomba de corriente (GPIO17) no tiene el problema porque sus pines bajan por defecto.

**Por verificar.** Depende del módulo de relé: reiniciar la Pi con el servicio detenido y observar si el relé de llenado se activa.

**Opciones:**

- **Sin recablear:** añadir `gpio=4=op,dl` a `/boot/firmware/config.txt`, que deja el pin como salida en bajo desde el inicio del arranque. Documentarlo en [setup.md](setup.md). Falta comprobar qué pasa con el pin cuando el servicio lo libera al detenerse.
- **Recableando:** mover el relé a un pin con *pull-down* por defecto, por ejemplo `J8:16` (GPIO23), y cambiar `RELE_LLENADO` en `config.py`. Es la solución completa (igual que se hizo con el motor NEMA).

## 2. Lista de puesta en marcha

Escribir `docs/puesta-en-marcha.md` con las comprobaciones en la Pi, en orden, para no saltarse ninguna. Debe incluir todo lo de la sección [Comprobaciones en la Pi](#comprobaciones-en-la-pi).

## 3. Contraseña en texto claro

El panel usa HTTP Basic sobre HTTP: la contraseña viaja codificada, no cifrada, y cualquiera que capture el tráfico de la red local puede leerla. Aceptable en una red de confianza. Si no lo es, poner un proxy inverso con HTTPS delante (por ejemplo Caddy) y que el servidor escuche solo en `127.0.0.1` (`HOST` en `config.py`).

## 4. Carpeta del peso en `/dev/shm`

`/dev/shm` es escribible por todos los usuarios. Otro usuario de la Pi podría crear antes `/dev/shm/polyethylene-tank` y falsear el peso que muestra el panel (solo eso: no controla nada). En una Pi de un solo usuario el riesgo es mínimo. Solución: crear la carpeta con permisos `700` y comprobar que pertenece al usuario del servicio, o usar `RuntimeDirectory=` de systemd en los dos servicios.

## 5. Prioridad de tiempo real para la balanza

`libhx711` lee con más precisión con prioridad de tiempo real, que solo obtiene con privilegios (su documentación indica `sudo`). Si las lecturas son ruidosas, probar a dar al servicio de la balanza la capacidad `CAP_SYS_NICE` (`AmbientCapabilities=CAP_SYS_NICE` en el `.service`) y comprobar si mejora. Por verificar que la librería la aproveche así.

## 6. Alertas

Avisar por correo o Telegram cuando el ciclo se detiene por un error (por ejemplo, el tanque no se llenó), para no tener que vigilar el panel. El punto de enganche es `Tank._cycle`, donde ya se registra el error.

## 7. Historial de ciclos

Guardar los ciclos completados (fecha, duración, errores) para ver la producción por día. Hoy el contador vive en memoria y se reinicia con el servicio.

## 8. Actualizaciones automáticas de dependencias

Activar Dependabot en GitHub (`.github/dependabot.yml`, con `package-ecosystem: "uv"` y `"github-actions"`) para recibir pull requests con las actualizaciones; la CI las probará.

## Comprobaciones en la Pi

Cosas que el código ya hace pero que solo se pueden comprobar con el hardware (la CI usa pines simulados):

- [ ] Mover los cables del motor NEMA: STEP del pin físico 3 al 13, DIR del 5 al 15. Probar con `tools/try_nema.py`.
- [ ] Crear `/etc/polyethylene-tank.env` con una contraseña y comprobar que el panel la pide.
- [ ] Desconectar el fin de carrera y comprobar que el llenado se detiene con el error "El tanque no se llenó".
- [ ] Pulsar el botón físico PARAR durante un ciclo: bombas y motor deben apagarse al instante.
- [ ] Pulsar el botón físico INICIAR con la máquina parada.
- [ ] Instalar `libhx711` con `scripts/install-hx711.sh` y comprobar que `uv sync --extra scale` compila `hx711-rpi-py`.
- [ ] Comprobar que `float()` sobre el peso de `hx711-rpi-py` devuelve el número esperado (en `scale.py`).
- [ ] Recalibrar la balanza con `calibrate.py` (ver [hardware.md](hardware.md)); hoy se usa el valor antiguo `-7627`.
- [ ] Comprobar que el panel muestra el peso y que dice "sin datos" al detener la balanza.
- [ ] Comprobar la pantalla LCD con las versiones nuevas de `RPLCD` (1.4.0) y `smbus2` (0.6.1).
- [ ] Confirmar si el servo `túnel` es de rotación continua (se dedujo por sus tiempos fijos).
- [ ] Opcional: activar pigpio y comprobar que los servos dejan de vibrar.
