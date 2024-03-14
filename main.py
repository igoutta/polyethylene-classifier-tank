from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import Button, LED, Servo, AngularServo, PhaseEnableMotor
from time import sleep
from multiprocessing import Process
import sys


def main():
    print("Activando bomba y cerrando valvulas de desfogue")
    bomba_llenado.on()
    servo_sapo.mid()
    servo_tunel.mid()
    print("Esperar que se llene el tanque para hacer separaración")
    TIEMPO_LLENADO = 8
    sensor_limite.wait_for_press(timeout=TIEMPO_LLENADO)
    print("Inicia la clasificación")
    bomba_llenado.off()
    bomba_corriente.on()
    motor_nema.forward(speed=0.99)  # 0.99 es llo máximo
    TIEMPO_LIMPIEZA_SEC = 120
    sleep(TIEMPO_LIMPIEZA_SEC)
    print("Inicia el desfogue por el tubo de escape")
    motor_nema.stop()
    servo_sapo.max()
    TIEMPO_DESFOGUE_SEC = 15
    sleep(TIEMPO_DESFOGUE_SEC)
    print("Cierra el tubo de escape y apaga la corriente")
    bomba_corriente.off()
    servo_sapo.mid()
    TIEMPO_FINAL_SEC = 20
    sleep(TIEMPO_FINAL_SEC)
    print("Limpia residuos del tubo")
    servo_tunel.max()
    sleep(1)
    print("Termina el proceso")
    servo_tunel.mid()
    sleep(0.5)


def stop():
    print("Termina subidamente el subproceso principal")
    main_process.kill()
    print("Apaga todos los actuadores")
    bomba_llenado.off()
    bomba_corriente.off()
    motor_nema.stop()
    servo_sapo.mid()
    sleep(5)
    servo_tunel.mid()
    sleep(0.5)


def safe_exit(signum, frame):
    sys.exit(1)


# Declaración de pines
INICIAR = "J8:37"
PARAR = "J8:35"
FIN_CARRERA = "J8:19"
RELE_LLENADO = "J8:7"
RELE_CORRIENTE = "J8:11"
NEMA_STEP = "J8:3"
NEMA_DIR = "J8:5"
# *PWM
SAPO = "J8:33"
TUNEL = "J8:32"

# Instanciación de variables
boton_activar = Button(pin=INICIAR, bounce_time=0.3)
boton_parar = Button(pin=PARAR, bounce_time=0.3)
sensor_limite = Button(pin=FIN_CARRERA, pull_up=False, bounce_time=0.3)

servo_sapo = AngularServo(pin=SAPO, initial_angle=0)
servo_tunel = Servo(pin=TUNEL, initial_value=0)

motor_nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)

bomba_llenado = LED(pin=RELE_LLENADO)
bomba_corriente = LED(pin=RELE_CORRIENTE)

# Procesamiento
main_process: Process = Process(target=main, name="Principal")


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    boton_parar.when_pressed = stop
    if (
        boton_activar.is_pressed
        and not main_process.is_alive()
        and not boton_parar.is_pressed
    ):
        main_process.start()

    pause()

except KeyboardInterrupt:
    pass

finally:
    print("\nTermina la secuencia del proceso sí esta corriendo")
    if main_process.is_alive():
        main_process.terminate()
    main_process.close()
    print("Finaliza todas las conexiones")
    bomba_llenado.off()
    bomba_corriente.off()
    bomba_llenado.close()
    bomba_corriente.close()
    motor_nema.stop()
    motor_nema.close()
    servo_sapo.mid()
    servo_tunel.mid()
    servo_sapo.close()
    servo_tunel.close()
    sensor_limite.close()
    boton_parar.close()
    boton_activar.close()
