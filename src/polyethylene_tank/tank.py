"""Hardware y ciclo de limpieza del tanque clasificador de polietileno."""

import warnings
from threading import Event, Lock, Thread
from time import sleep

from gpiozero import LED, AngularServo, Button, PhaseEnableMotor, Servo

from .config import (
    FIN_CARRERA,
    INICIAR,
    NEMA_DIR,
    NEMA_STEP,
    PARAR,
    RELE_CORRIENTE,
    RELE_LLENADO,
    SAPO,
    TIEMPO_DESFOGUE_SEC,
    TIEMPO_LIMPIEZA_SEC,
    TIEMPO_LLENADO_SEC,
    TUNEL,
)

warnings.filterwarnings("ignore")


class Tank:
    def __init__(self):
        self.boton_activar = Button(pin=INICIAR)
        self.boton_parar = Button(pin=PARAR)
        self.sensor_limite = Button(pin=FIN_CARRERA, pull_up=False, bounce_time=5)

        self.servo_sapo = AngularServo(pin=SAPO, initial_angle=0)
        self.servo_sapo.detach()
        self.servo_tunel = Servo(pin=TUNEL, initial_value=0)
        self.servo_tunel.detach()  # Importante

        self.motor_nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)

        self.bomba_llenado = LED(RELE_LLENADO)
        self.bomba_corriente = LED(RELE_CORRIENTE)

        self.step = "Detenido"
        self._thread = None
        self._stop_event = Event()
        self._lock = Lock()

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        with self._lock:
            if self.running:
                return
            self._stop_event.clear()
            self._thread = Thread(target=self._cycle, name="Principal", daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop_event.set()
            if self._thread is not None:
                print("Termina el hilo principal")
                self._thread.join()
                self._thread = None
            print("Apaga todos los actuadores")
            self.step = "Deteniendo"
            self.bomba_llenado.off()
            self.bomba_corriente.off()
            self.motor_nema.stop()
            self.servo_sapo.min()
            sleep(2)
            self.servo_sapo.detach()
            self._limpiar_tubo()
            self.step = "Detenido"

    def close(self):
        try:
            self.stop()
        finally:
            print("Finaliza todas las conexiones")
            for device in (
                self.bomba_llenado,
                self.bomba_corriente,
                self.motor_nema,
                self.servo_sapo,
                self.servo_tunel,
                self.sensor_limite,
                self.boton_parar,
                self.boton_activar,
            ):
                device.close()

    def _wait(self, seconds):
        """Espera interrumpible: devuelve True si se pidió parar."""
        return self._stop_event.wait(seconds)

    def _limpiar_tubo(self):
        self.servo_tunel.min()
        sleep(1.7)
        self.servo_tunel.max()
        sleep(0.95)
        self.servo_tunel.detach()  # Para asegurar que este apagado

    def _cycle(self):
        # El ciclo se repite hasta que se pida parar
        while not self._stop_event.is_set():
            self.step = "Llenando el tanque"
            print("Activando bomba y cerrando valvulas de desfogue")
            self.bomba_llenado.on()
            lleno = False
            for _ in range(TIEMPO_LLENADO_SEC * 10):
                if self.sensor_limite.is_pressed:
                    lleno = True
                    break
                if self._wait(0.1):
                    return
            if not lleno:
                print("AVISO: el sensor no detectó el tanque lleno a tiempo")

            self.step = "Clasificando"
            print("Inicia la clasificación")
            self.bomba_llenado.off()
            self.bomba_corriente.on()
            self.motor_nema.forward(speed=0.95)  # 0.9 es lo óptimo
            if self._wait(TIEMPO_LIMPIEZA_SEC):
                return

            self.step = "Desfogando"
            print("Inicia el desfogue por el tubo de escape")
            self.motor_nema.stop()
            if self._wait(2):
                return
            self.servo_sapo.max()
            if self._wait(TIEMPO_DESFOGUE_SEC):
                return

            self.step = "Limpiando el tubo"
            print("Cierra el tubo de escape y apaga la corriente")
            self.bomba_corriente.off()
            self.servo_sapo.min()
            sleep(1)
            self.servo_sapo.detach()
            self._limpiar_tubo()
            print("Termina el ciclo")
