"""Prueba de banco del motor NEMA: `uv run --extra pi python tools/try_nema.py`"""

from contextlib import suppress
from time import sleep

from gpiozero import PhaseEnableMotor

from polyethylene_tank.config import NEMA_DIR, NEMA_STEP

nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)

try:
    # Ctrl-C es la forma normal de terminar la prueba, no un error
    with suppress(KeyboardInterrupt):
        while True:
            nema.forward(speed=0.95)  # ni 0.999 ni 0.95 ni 1
            sleep(45)
            nema.reverse()
            sleep(45)
finally:
    nema.stop()
    sleep(1)
    nema.close()
