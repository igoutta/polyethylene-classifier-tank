from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import Button, LED, Servo, AngularServo, PhaseEnableMotor
from time import sleep
from multiprocessing import Process
import warnings
import sys


def main():
    print("Activando bomba y cerrando valvulas de desfogue")
    bomba_llenado.on()
    print("Esperar que se llene el tanque para hacer separaración")
    TIEMPO_LLENADO = 15
    sensor_limite.wait_for_press(timeout=TIEMPO_LLENADO)
    print("Inicia la clasificación")
    bomba_llenado.off()
    bomba_corriente.on()
    motor_nema.forward(speed=0.99)  # 0.99 es lo óptimo
    TIEMPO_LIMPIEZA_SEC = 120
    sleep(TIEMPO_LIMPIEZA_SEC)
    print("Inicia el desfogue por el tubo de escape")
    motor_nema.stop()
    servo_sapo.max()
    TIEMPO_DESFOGUE_SEC = 15
    sleep(TIEMPO_DESFOGUE_SEC)
    print("Cierra el tubo de escape y apaga la corriente")
    bomba_corriente.off()
    servo_sapo.min()
    sleep(1)
    servo_sapo.detach()
    print("Limpia residuos del tubo")
    servo_tunel.min()
    sleep(1.7)
    servo_tunel.max()
    sleep(1.1)
    servo_tunel.detach()  # Para asegurar que este apagado
    print("Termina el proceso")


def stop():
    blocking = True
    while blocking:
        print("Termina súbitamente el subproceso principal")
        if main_process.is_alive():
            main_process.terminate()
        sleep(0.1)
        print("Apaga todos los actuadores")
        bomba_llenado.off()
        bomba_corriente.off()
        motor_nema.stop()
        servo_sapo.min()
        sleep(2)
        servo_sapo.detach()
        servo_tunel.min()
        sleep(1.7)
        servo_tunel.max()
        sleep(1.1)
        servo_tunel.detach()
        blocking = False


def safe_exit(signum, frame):
    sys.exit(1)


warnings.filterwarnings("ignore")

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

# Instanciación de pines
boton_activar = Button(pin=INICIAR, bounce_time=5)
boton_parar = Button(pin=PARAR, bounce_time=5)
sensor_limite = Button(pin=FIN_CARRERA, pull_up=False, bounce_time=5)

servo_sapo = AngularServo(pin=SAPO, initial_angle=0)
servo_sapo.detach()
servo_tunel = Servo(pin=TUNEL, initial_value=0)
servo_tunel.detach()  # Importante

motor_nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)

bomba_llenado = LED(pin=RELE_LLENADO)
bomba_corriente = LED(pin=RELE_CORRIENTE)

# Instancias de procesamiento
blocking = False
main_process: Process = Process(target=main, name="Principal", daemon=True)

try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    boton_parar.when_pressed = stop
    if boton_activar.is_pressed and not main_process.is_alive() and not blocking:
        main_process.start()

    pause()

except KeyboardInterrupt:
    if main_process.is_alive():
        main_process.join(2)

finally:
    stop()
    print("Finaliza todas las conexiones")
    main_process.close()

    bomba_llenado.close()
    bomba_corriente.close()

    motor_nema.close()
    servo_sapo.close()
    servo_tunel.close()

    sensor_limite.close()
    boton_parar.close()
    boton_activar.close()
