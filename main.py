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
from time import monotonic, sleep
import sys

# Declaración de pines
INICIAR = "J8:38"
PARAR = "J8:40"
FIN_CARRERA = "J8:36"
RELE_BOMBA = "J8:7"
NEMA_STEP = "J8:3"
NEMA_DIR = "J8:5"
# *PWM
SAPO = "J8:32"
TUNEL = "J8:33"
CERRADO = -1
ABIERTO = 1

# Instanciación de variables
boton_activar = Button(INICIAR)
boton_parar = Button(PARAR)
sensor_limite = DigitalInputDevice(FIN_CARRERA)
bomba = DigitalOutputDevice(RELE_BOMBA)
motor_nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)
servo_sapo = Servo(pin=SAPO, initial_value=CERRADO)
servo_tunel = Servo(pin=TUNEL, initial_value=ABIERTO)
tiempo_inicio: float = None
tiempo_fin: float = None


def start():
    # Condición necesaria para desfogar
    bomba.on()  # Activar la bomba para cumplir la condición
    sensor_limite.wait_for_active()
    # Determinar tiempos para medir
    if tiempo_inicio is None:
        tiempo_inicio = monotonic()
        tiempo_fin = monotonic()
    TIEMPO_DESFOGUE_SEC = 120
    # Desfogue
    while (tiempo_fin - tiempo_inicio) < TIEMPO_DESFOGUE_SEC:
        bomba.off()
        motor_nema.forward(speed=1)
        servo_tunel.value = CERRADO
        servo_sapo.value = ABIERTO
        tiempo_fin = monotonic()
    # Final de desfogue
    else:
        bomba.on()
        tiempo_inicio = None
        servo_sapo.value = CERRADO
        sleep(1.5)
        servo_tunel.value = ABIERTO


def stop():
    bomba.off()
    motor_nema.stop()
    servo_sapo.value = CERRADO
    servo_tunel.value = ABIERTO


def emergency_stop():
    boton_parar.when_pressed = stop
    pause()


def safe_exit(signum, frame):
    sys.exit(1)


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    parada = threading.Thread(name="Parada de emergencia", target=stop)
    parada.start()

    boton_activar.when_pressed = start

    pause()

except KeyboardInterrupt:
    pass

finally:
    pass
