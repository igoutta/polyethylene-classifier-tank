# Tanque clasificador de polietileno

Control de un tanque que separa polietileno del resto del material, en una Raspberry Pi 4. Un panel web (o los botones físicos) inicia y detiene el ciclo, y un servicio aparte mide el peso con una balanza (HX711) y lo muestra en una pantalla LCD y en el panel.

## Estructura

```text
src/polyethylene_tank/
    config.py      pines, tiempos por defecto, rutas y calibración
    tank.py        hardware y ciclo de limpieza (clase Tank)
    settings.py    tiempos del ciclo validados y guardados en disco
    app.py         API FastAPI + panel web (con contraseña opcional)
    static/        página del panel (sin dependencias externas)
    scale.py       balanza con LCD I2C (servicio independiente)
    weight.py      último peso, compartido entre la balanza y el panel
    files.py       escritura atómica de archivos
    __main__.py    arranque del servidor
tests/             pruebas con pines simulados
tools/             scripts de banco (servos, motor NEMA)
scripts/           instalación de libhx711 en la Pi
firmware/          alternativa de la balanza en Arduino
deploy/            servicios de systemd y archivo de entorno de ejemplo
.github/           CI: lint, tipos, complejidad y pruebas en cada push
docs/              instalación, hardware, red y problemas frecuentes
```

## El ciclo

Al presionar COMENZAR (en el panel o el botón físico) el ciclo se repite hasta presionar PARAR:

1. **Llenado:** bomba de llenado encendida hasta que el final de carrera detecta el tanque lleno. Si no lo detecta en el tiempo máximo (15 s por defecto), **se detiene todo con un error** en el panel.
2. **Clasificación:** bomba de corriente y motor NEMA (60 s por defecto).
3. **Desfogue:** el motor se detiene y el servo `sapo` abre el tubo de escape (15 s por defecto).
4. **Cierre y limpieza:** se cierra el tubo, se apaga la bomba y el servo `túnel` limpia los residuos.

PARAR corta de inmediato las bombas y el motor y luego deja los servos en reposo. El botón físico PARAR funciona aunque el panel o la red no respondan.

Cualquier error inesperado detiene la máquina y se muestra en el panel. Los tiempos se cambian desde el panel (sección *Tiempos del ciclo*), se aplican desde la próxima etapa y se guardan en disco. El panel también muestra los ciclos completados y el peso de la balanza.

## Uso

Requiere [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```sh
uv run --extra pi tank-server            # panel en http://<ip-de-la-pi>:8080
uv run --extra scale tank-scale          # balanza con LCD (antes: scripts/install-hx711.sh)
```

El servidor usa un solo proceso porque el hardware no se puede compartir. Las opciones del servicio van en `/etc/polyethylene-tank.env` (copiar [deploy/polyethylene-tank.env.example](deploy/polyethylene-tank.env.example)):

- `TANK_PASSWORD` (y `TANK_USER`, por defecto `admin`): el panel pide usuario y contraseña. Sin ella queda abierto a la red.
- `GPIOZERO_PIN_FACTORY=pigpio`: servos sin vibración en la Pi 4. Viene comentada (con `#` delante); se activa borrando el `#`, después de instalar `pigpiod`.

Pasos completos en [docs/setup.md](docs/setup.md).

| API | |
|---|---|
| `GET /api/status` | estado, paso, error, ciclos completados, último ciclo y peso |
| `POST /api/start` / `POST /api/stop` | iniciar / detener |
| `GET /api/tiempos` / `PUT /api/tiempos` | leer / cambiar los tiempos (0 < t ≤ 600 s) |

## Desarrollo (sin Raspberry Pi)

```sh
uv sync --extra scale
GPIOZERO_PIN_FACTORY=mock GPIOZERO_MOCK_PIN_CLASS=mockpwmpin uv run tank-server

uv run pytest          # pruebas
uv run ruff check .    # lint (complejidad ciclomática máxima de 6, sin print)
uv run ruff format .
uv run ty check        # tipos
uv run complexipy      # complejidad cognitiva (máximo 8)
```

La CI de GitHub ejecuta los mismos pasos en cada push.

## Documentación

- [docs/setup.md](docs/setup.md): instalación en la Pi y servicios de systemd (`deploy/`)
- [docs/hardware.md](docs/hardware.md): pines, conexiones y calibración de la balanza
- [docs/network.md](docs/network.md): conectar la Pi a una red Wi-Fi
- [docs/troubleshooting.md](docs/troubleshooting.md): problemas frecuentes
- [docs/backlog.md](docs/backlog.md): mejoras pendientes y comprobaciones por hacer en la Pi
