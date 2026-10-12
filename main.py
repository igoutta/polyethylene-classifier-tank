from signal import signal, SIGTERM, SIGHUP
from gpiozero import Button, LED, Servo, AngularServo, PhaseEnableMotor
from time import sleep
from threading import Thread, Event, Lock
import warnings
import sys
import http.server
import socketserver


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Solo se sirve la página de control, nada más del directorio
        estado = "EN EJECUCIÓN" if is_running() else "DETENIDO"
        with open("index.html", encoding="utf-8") as f:
            body = f.read().replace("{{estado}}", estado).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # Las acciones usan POST para que recargar la página no las repita
        if self.path == "/start":
            start()
        elif self.path == "/stop":
            stop()
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format, *args):
        print(self.address_string(), format % args)


def wait(seconds):
    """Espera interrumpible: devuelve True si se pidió parar."""
    return stop_event.wait(seconds)


def main():
    # El ciclo se repite hasta que se presione PARAR
    while not stop_event.is_set():
        print("Activando bomba y cerrando valvulas de desfogue")
        bomba_llenado.on()
        print("Esperar que se llene el tanque para hacer separación")
        TIEMPO_LLENADO = 15
        lleno = False
        for _ in range(TIEMPO_LLENADO * 10):
            if sensor_limite.is_pressed:
                lleno = True
                break
            if wait(0.1):
                return
        if not lleno:
            print("AVISO: el sensor no detectó el tanque lleno a tiempo")
        print("Inicia la clasificación")
        bomba_llenado.off()
        bomba_corriente.on()
        motor_nema.forward(speed=0.95)  # 0.9 es lo óptimo
        TIEMPO_LIMPIEZA_SEC = 60
        if wait(TIEMPO_LIMPIEZA_SEC):
            return
        print("Inicia el desfogue por el tubo de escape")
        motor_nema.stop()
        if wait(2):
            return
        servo_sapo.max()
        TIEMPO_DESFOGUE_SEC = 15
        if wait(TIEMPO_DESFOGUE_SEC):
            return
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
        print("Termina el ciclo")


def is_running():
    return main_thread is not None and main_thread.is_alive()


def start():
    global main_thread
    with control_lock:
        if is_running():
            return
        stop_event.clear()
        main_thread = Thread(target=main, name="Principal", daemon=True)
        main_thread.start()


def stop():
    global main_thread
    with control_lock:
        stop_event.set()
        if main_thread is not None:
            print("Termina el hilo principal")
            main_thread.join()
            main_thread = None
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

# Estado del ciclo principal
main_thread = None
stop_event = Event()
control_lock = Lock()
# Server
PORT = 8080


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    with Server(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

finally:
    try:
        stop()
    finally:
        print("Finaliza todas las conexiones")
        for device in (
            bomba_llenado,
            bomba_corriente,
            motor_nema,
            servo_sapo,
            servo_tunel,
            sensor_limite,
            boton_parar,
            boton_activar,
        ):
            device.close()
