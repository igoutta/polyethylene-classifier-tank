#!/usr/bin/python3

from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import (
    Button,
    LED,
    Servo,
    PhaseEnableMotor,
)
from time import monotonic, sleep
import multiprocessing
import sys


def main():
    bomba_llenado.on()  # Activar la bomba para cumplir la condición
    servo_sapo.value = CERRADO  # Cerrar para cumplir condición
    servo_tunel.value = CERRADO  # Cerrar para cumplir condición
    custom_sleep(1)
    sensor_limite.wait_for_press()  # Condición necesaria para desfogar
    # Limpieza
    bomba_llenado.off()  # Apagar para no desbordar
    bomba_corriente.on()  # Prender para circular el agua
    motor_nema.forward(speed=1)  # Limpiar
    TIEMPO_LIMPIEZA_SEC = 120
    custom_sleep(TIEMPO_LIMPIEZA_SEC)
    motor_nema.stop()  # Apagar para desfogue
    servo_sapo.value = ABIERTO
    TIEMPO_DESFOGUE_SEC = 15
    custom_sleep(TIEMPO_DESFOGUE_SEC)
    servo_sapo.value = CERRADO
    TIEMPO_FINAL_SEC = 10
    custom_sleep(TIEMPO_FINAL_SEC)
    servo_tunel.value = ABIERTO
    custom_sleep(1)
    # Parada total de desfogue
    stop()


def custom_sleep(tiempo: float):
    tiempos["inicio"] = monotonic()
    tiempos["fin"] = monotonic()
    while not boton_parar.is_pressed and (
        (tiempos["fin"] - tiempos["inicio"]) < tiempo
    ):
        tiempos["fin"] = monotonic()


def stop():
    main_process.kill()
    bomba_llenado.off()
    bomba_corriente.off()
    motor_nema.stop()
    servo_sapo.value = CERRADO
    sleep(2)
    servo_tunel.value = CERRADO
    sleep(0.02)


def safe_exit(signum, frame):
    sys.exit(1)


# Declaración de pines
INICIAR = "J8:38"
PARAR = "J8:40"
FIN_CARRERA = "J8:36"
GALGA_DATA = "J8:21"
GALGA_CLK = "J8:23"
LCD_SDA = "J8:3"
LCD_SCK = "J8:5"
RELE_LLENADO = "J8:7"
RELE_CORRIENTE = "J8:11"
NEMA_STEP = "J8:13"
NEMA_DIR = "J8:15"
# *PWM
SAPO = "J8:32"
TUNEL = "J8:33"
CERRADO = -1
ABIERTO = 1

# Instanciación de variables
boton_activar = Button(INICIAR)
boton_parar = Button(PARAR)
sensor_limite = Button(FIN_CARRERA)
bomba_llenado = LED(RELE_LLENADO)
bomba_corriente = LED(RELE_CORRIENTE)
motor_nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)
servo_sapo = Servo(pin=SAPO, initial_value=CERRADO)
servo_tunel = Servo(pin=TUNEL, initial_value=CERRADO)

# Procesamiento
tiempos = {"inicio": None, "fin": None}
main_process = multiprocessing.Process(target=main)


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    boton_activar.when_pressed = main_process.start
    boton_parar.when_pressed = stop

    pause()

except KeyboardInterrupt:
    pass

finally:
    if main_process.is_alive:
        main_process.terminate()
    main_process.close()
    bomba_llenado.off()
    bomba_corriente.off()
    bomba_llenado.close()
    bomba_corriente.close()
    motor_nema.stop()
    motor_nema.close()
    servo_sapo.close()
    servo_tunel.close()
