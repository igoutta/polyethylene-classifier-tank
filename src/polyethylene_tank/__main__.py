"""Arranca el servidor: `uv run tank-server` o `python -m polyethylene_tank`."""

import uvicorn

from .config import HOST, PORT


def main():
    # Un solo worker: el hardware (GPIO) no se puede compartir entre procesos
    uvicorn.run("polyethylene_tank.app:app", host=HOST, port=PORT, workers=1)


if __name__ == "__main__":
    main()
