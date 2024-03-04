#!/usr/bin/python3

from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import (
    Button,
    DigitalInputDevice,
    DigitalOutputDevice,
    Servo,
    PhaseEnableMotor,
)
import threading

iniciar = Button(2)
parar = Button(3)
sensor_limite = DigitalInputDevice(4)
bomba = DigitalOutputDevice(12)
motor_escobilla = PhaseEnableMotor(9, 12)
servo_sapo = Servo(9)
servo_tunel = Servo(11)


def safe_exit(signum, frame):
    exit(1)


def start():
    sensor_limite.wait_for_active()

    print("Hello!")


def stop():
    if parar.is_held:
        bomba.value = False
        servo_sapo.value = 0
        servo_tunel.value = 0

    pause()


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    parada = threading.Thread(name="Parada de emergencia", target=stop)
    parada.start()
    iniciar.when_pressed = start

    pause()

except KeyboardInterrupt:
    pass

finally:
    pass
