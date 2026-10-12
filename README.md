# Tanque clasificador de polietileno

Control de un tanque que separa polietileno del resto del material, en una Raspberry Pi. Un panel web inicia y detiene el ciclo, y un servicio aparte muestra el peso de una balanza (HX711) en una pantalla LCD.

## Estructura

```text
src/polyethylene_tank/
    config.py      pines, tiempos del ciclo y calibración de la balanza
    tank.py        hardware y ciclo de limpieza (clase Tank)
    app.py         API FastAPI + panel web
    static/        página del panel (sin dependencias externas)
    scale.py       balanza con LCD I2C (servicio independiente)
    __main__.py    arranque del servidor
tests/             pruebas con pines simulados
tools/             scripts de banco (servos, motor NEMA)
scripts/           instalación de libhx711 en la Pi
firmware/          alternativa de la balanza en Arduino
deploy/            servicios de systemd
docs/              instalación, hardware, red y problemas frecuentes
```

## El ciclo

Al presionar COMENZAR el ciclo se repite hasta presionar PARAR:

1. **Llenado:** bomba de llenado encendida hasta que el final de carrera detecta el tanque lleno (máximo 15 s).
2. **Clasificación:** bomba de corriente y motor NEMA durante 60 s.
3. **Desfogue:** el motor se detiene y el servo `sapo` abre el tubo de escape 15 s.
4. **Cierre y limpieza:** se cierra el tubo, se apaga la bomba y el servo `túnel` limpia los residuos.

PARAR interrumpe la etapa en curso, apaga las bombas y el motor y deja los servos en reposo.

## Uso

Requiere [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```sh
uv run --extra pi tank-server            # panel en http://<ip-de-la-pi>:8080
uv run --extra scale tank-scale          # balanza con LCD (antes: scripts/install-hx711.sh)
```

El servidor usa un solo proceso porque el hardware no se puede compartir. API: `GET /api/status`, `POST /api/start`, `POST /api/stop`.

## Desarrollo (sin Raspberry Pi)

```sh
uv sync --extra scale
GPIOZERO_PIN_FACTORY=mock GPIOZERO_MOCK_PIN_CLASS=mockpwmpin uv run tank-server

uv run pytest          # pruebas
uv run ruff check .    # lint (incluye complejidad ciclomática máxima de 6)
uv run ruff format .
uv run ty check        # tipos
```

## Documentación

- [docs/setup.md](docs/setup.md): instalación en la Pi y servicios de systemd (`deploy/`)
- [docs/hardware.md](docs/hardware.md): pines, conexiones y calibración de la balanza
- [docs/network.md](docs/network.md): conectar la Pi a una red Wi-Fi
- [docs/troubleshooting.md](docs/troubleshooting.md): problemas frecuentes
