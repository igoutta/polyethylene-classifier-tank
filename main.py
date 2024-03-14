from signal import signal, SIGTERM, SIGHUP, pause
from gpiozero import Button, LED, Servo, AngularServo, PhaseEnableMotor
from time import sleep
from multiprocessing import Process
import warnings
import sys
import http.server
import socketserver


# here you create a new handler, you had a new way to handle get request
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        # this code execute when a GET request happen, then you have to check if the request happenned because the user pressed the button
        if self.path.find("Start=true") != -1:
            main_process.start()
        if self.path.find("Stop=true") != -1:
            stop()
        return super().do_GET()


def main():
    while True:
        print("Activando bomba y cerrando valvulas de desfogue")
        bomba_llenado.on()
        print("Esperar que se llene el tanque para hacer separación")
        TIEMPO_LLENADO = 15
        sensor_limite.wait_for_press(timeout=TIEMPO_LLENADO)
        print("Inicia la clasificación")
        bomba_llenado.off()
        bomba_corriente.on()
        motor_nema.forward(speed=0.95)  # 0.9 es lo óptimo
        TIEMPO_LIMPIEZA_SEC = 60
        sleep(TIEMPO_LIMPIEZA_SEC)
        print("Inicia el desfogue por el tubo de escape")
        motor_nema.stop()
        sleep(2)
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
        sleep(0.95)
        servo_tunel.detach()  # Para asegurar que este apagado
        print("Termina el proceso")


def stop():
    running = True
    while running:
        print("Termina súbitamente el subproceso principal")
        main_process.terminate()
        main_process.join()
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
        sleep(0.95)
        servo_tunel.detach()
        running = False


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
boton_activar = Button(pin=INICIAR)
boton_parar = Button(pin=PARAR)
sensor_limite = Button(pin=FIN_CARRERA, pull_up=False, bounce_time=5)

servo_sapo = AngularServo(pin=SAPO, initial_angle=0)
servo_sapo.detach()
servo_tunel = Servo(pin=TUNEL, initial_value=0)
servo_tunel.detach()  # Importante

motor_nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)

bomba_llenado = LED(RELE_LLENADO)
bomba_corriente = LED(RELE_CORRIENTE)

# Instancias de procesamiento
main_process = Process(target=main, name="Principal", daemon=True)
# Server
PORT = 8080
myHandler = Handler


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    # boton_parar.when_pressed = stop
    # if boton_activar.is_pressed and not main_process.is_alive() and not running:
    #    main_process.start()

    with socketserver.TCPServer(("", PORT), myHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

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
