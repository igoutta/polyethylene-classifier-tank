"""Arranca el servidor: `uv run tank-server` o `python -m polyethylene_tank`."""

import logging

import uvicorn

from .config import HOST, LOG_FORMAT, PORT


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    # Un solo worker: el hardware (GPIO) no se puede compartir entre procesos
    uvicorn.run("polyethylene_tank.app:app", host=HOST, port=PORT, workers=1)


if __name__ == "__main__":
    main()
