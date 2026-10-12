"""Prueba de banco de los servos: `uv run --extra pi python tools/config_servos.py`"""

import warnings
from contextlib import suppress
from time import sleep

from gpiozero import AngularServo, Servo

from polyethylene_tank.config import SAPO, TUNEL

warnings.filterwarnings("ignore")

# from gpiozero.pins.pigpio import PiGPIOFactory
# factory = PiGPIOFactory()
servo_sapo = AngularServo(pin=SAPO, initial_angle=0)  # pin_factory=factory)
servo_tunel = Servo(pin=TUNEL, initial_value=0)  # pin_factory=factory)

try:
    # Ctrl-C es la forma normal de terminar la prueba, no un error
    with suppress(KeyboardInterrupt):
        while True:
            servo_tunel.detach()
            servo_sapo.min()
            sleep(2)
            servo_sapo.max()
            sleep(2)
            servo_sapo.detach()
            servo_tunel.min()
            sleep(1.7)
            servo_tunel.max()
            sleep(0.95)
            servo_tunel.detach()
finally:
    servo_sapo.close()
    servo_tunel.close()
