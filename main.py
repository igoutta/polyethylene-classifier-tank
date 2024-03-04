#!/usr/bin/python3

from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import Button, DigitalInputDevice, DigitalOutputDevice, Servo, Motor
import threading

iniciar = Button(2)
parar = Button(3)
sensor_limite = DigitalInputDevice(4)
bomba = DigitalOutputDevice(12)
motor_escobilla = Motor(9)
servo_sapo = Servo(9)
servo_tunel = Servo(11)


def safe_exit(signum, frame):
    exit(1)


def start():
    sensor_limite.wait_for_active()

    print("Hello!")


def stop():
    print("Parar")


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    comenzar = threading.Thread(name="Estado Activo", target=start)
    parar.when_pressed = stop
    iniciar.when_pressed = comenzar.start

    pause()

except KeyboardInterrupt:
    pass

finally:
    pass
