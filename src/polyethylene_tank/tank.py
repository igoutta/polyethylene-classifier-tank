"""Hardware y ciclo de limpieza del tanque clasificador de polietileno."""

import logging
import warnings
from threading import Event, Lock, Thread
from time import monotonic, sleep

from gpiozero import LED, AngularServo, Button, PhaseEnableMotor, Servo

from .config import (
    FIN_CARRERA,
    FIN_CARRERA_BOUNCE_SEC,
    INICIAR,
    NEMA_DIR,
    NEMA_STEP,
    PARAR,
    RELE_CORRIENTE,
    RELE_LLENADO,
    SAPO,
    TUNEL,
)
from .settings import Tiempos

warnings.filterwarnings("ignore")
log = logging.getLogger(__name__)

PAUSA_MOTOR_SEC = 2  # espera a que el motor se detenga antes de desfogar
SONDEO_SENSOR_SEC = 0.05


class FalloDeLlenado(RuntimeError):
    """El sensor de fin de carrera no detectó el tanque lleno a tiempo."""


class Tank:
    def __init__(self, tiempos=None):
        self.boton_activar = Button(pin=INICIAR)
        self.boton_parar = Button(pin=PARAR)
        self.sensor_limite = Button(
            pin=FIN_CARRERA, pull_up=False, bounce_time=FIN_CARRERA_BOUNCE_SEC
        )

        self.servo_sapo = AngularServo(pin=SAPO, initial_angle=0)
        self.servo_sapo.detach()
        self.servo_tunel = Servo(pin=TUNEL, initial_value=0)
        self.servo_tunel.detach()  # Importante

        self.motor_nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)

        self.bomba_llenado = LED(RELE_LLENADO)
        self.bomba_corriente = LED(RELE_CORRIENTE)

        self.tiempos = tiempos or Tiempos()
        self.step = "Detenido"
        self.error = None
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
            self.error = None
            self._stop_event.clear()
            self._thread = Thread(target=self._cycle, name="Principal", daemon=True)
            self._thread.start()

    def stop(self):
        # Bombas y motor se cortan ya, sin esperar a que el ciclo termine su paso
        self._stop_event.set()
        self._apagar_bombas()
        with self._lock:
            self._stop_event.set()
            self._join_cycle()
            self.step = "Deteniendo"
            self._apagar_actuadores()
            self.step = "Detenido"

    def close(self):
        try:
            self.stop()
        finally:
            log.info("Cierra todas las conexiones")
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

    def _join_cycle(self):
        if self._thread is None:
            return
        log.info("Espera a que termine el ciclo en curso")
        self._thread.join()
        self._thread = None

    def _apagar_bombas(self):
        self.bomba_llenado.off()
        self.bomba_corriente.off()
        self.motor_nema.stop()

    def _apagar_actuadores(self):
        log.info("Apaga todos los actuadores")
        self._apagar_bombas()
        self.servo_sapo.min()
        sleep(2)
        self.servo_sapo.detach()
        self._limpiar_tubo()

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
        try:
            self._repetir_etapas()
        except Exception as exc:
            # Cualquier fallo detiene la máquina y queda visible en el panel
            log.error(
                "Ciclo detenido por error: %s",
                exc,
                exc_info=not isinstance(exc, FalloDeLlenado),
            )
            self.error = str(exc) or type(exc).__name__
            self.step = "Apagando por error"
            self._apagar_actuadores()
            self.step = "Detenido por error"

    def _repetir_etapas(self):
        """Repite las etapas hasta que se pida parar."""
        etapas = (self._llenar, self._clasificar, self._desfogar, self._cerrar)
        while not self._stop_event.is_set():
            # Cada etapa devuelve False si se pidió parar durante su espera
            if not all(etapa() for etapa in etapas):
                return
            log.info("Termina el ciclo")

    def _llenar(self):
        self.step = "Llenando el tanque"
        log.info("Activa la bomba de llenado")
        self.bomba_llenado.on()
        limite = monotonic() + self.tiempos.llenado
        while monotonic() < limite:
            if self.sensor_limite.is_active:
                return True
            if self._wait(SONDEO_SENSOR_SEC):
                return False
        raise FalloDeLlenado(
            f"El tanque no se llenó en {self.tiempos.llenado:g} s: revisar el "
            "sensor de fin de carrera y la bomba de llenado"
        )

    def _clasificar(self):
        self.step = "Clasificando"
        log.info("Inicia la clasificación")
        self.bomba_llenado.off()
        self.bomba_corriente.on()
        self.motor_nema.forward(speed=0.95)  # 0.9 es lo óptimo
        return not self._wait(self.tiempos.limpieza)

    def _desfogar(self):
        self.step = "Desfogando"
        log.info("Inicia el desfogue por el tubo de escape")
        self.motor_nema.stop()
        if self._wait(PAUSA_MOTOR_SEC):
            return False
        self.servo_sapo.max()
        return not self._wait(self.tiempos.desfogue)

    def _cerrar(self):
        self.step = "Limpiando el tubo"
        log.info("Cierra el tubo de escape y apaga la corriente")
        self.bomba_corriente.off()
        self.servo_sapo.min()
        sleep(1)
        self.servo_sapo.detach()
        self._limpiar_tubo()
        return True
