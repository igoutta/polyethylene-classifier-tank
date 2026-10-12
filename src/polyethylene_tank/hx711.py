"""Driver mínimo del HX711 sobre los pines de gpiozero (lgpio).

Reemplaza a `hx711-rpi-py`, que obliga a compilar a mano una librería en C++
y solo declara soporte para Pi Zero/3/4. gpiozero ya elige el gpiochip correcto
(incluida la Pi 5), así que este driver no añade dependencias.

El HX711 se apaga si SCK permanece en alto más de ~60 µs. Python puede ser
interrumpido por el sistema en medio de un pulso, así que se mide cada pulso y
la lectura se descarta si alguno fue demasiado largo. Por eso las lecturas
públicas son siempre una mediana de varias muestras válidas.
"""

from statistics import median
from time import monotonic, perf_counter_ns, sleep

from gpiozero import Device

# Pulsos de reloj extra tras los 24 bits: seleccionan canal y ganancia
GAIN_PULSES = {128: 1, 32: 2, 64: 3}  # canal A=128/64, canal B=32

MAX_PULSE_NS = 50_000  # el chip se apaga a ~60 µs
# Con DOUT atascado en alto (cable suelto) se lee 0xFFFFFF; satura en ±0x7FFFFF
INVALID_RAW = {0xFFFFFF}


class HX711:
    def __init__(self, dout, sck, gain=128):
        """`dout` y `sck`: pines con `.state` (y `.function` si es gpiozero)."""
        if gain not in GAIN_PULSES:
            raise ValueError(f"ganancia no válida: {gain}")
        self._dout = dout
        self._sck = sck
        self._extra_pulses = GAIN_PULSES[gain]
        self.offset = 0
        self.reference_unit = 1

        self._sck.function = "output"
        self._dout.function = "input"
        self._sck.state = 0  # SCK en bajo = chip encendido

    @classmethod
    def from_gpio(cls, dout, sck, gain=128):
        """Crea el driver con pines BCM de la fábrica de gpiozero."""
        Device.ensure_pin_factory()
        factory = Device.pin_factory
        if factory is None:
            raise RuntimeError("gpiozero no tiene un pin factory disponible")
        return cls(factory.pin(dout), factory.pin(sck), gain)

    def close(self):
        for pin in (self._sck, self._dout):
            pin.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _ready(self):
        return not self._dout.state  # DOUT en bajo = conversión lista

    def read_raw(self, timeout=1.0):
        """Una lectura de 24 bits con signo, o None si el sample no es fiable.

        Lanza TimeoutError si el chip no tiene datos en `timeout` segundos.
        """
        limit = monotonic() + timeout
        while not self._ready():
            if monotonic() > limit:
                raise TimeoutError("HX711 sin datos: revisar cableado y alimentación")
            sleep(0.0005)

        value = 0
        longest = 0
        for _ in range(24 + self._extra_pulses):
            start = perf_counter_ns()
            self._sck.state = 1
            self._sck.state = 0
            longest = max(longest, perf_counter_ns() - start)
            value = (value << 1) | int(bool(self._dout.state))
        # Los pulsos de ganancia no son datos: el valor son los primeros 24 bits
        value >>= self._extra_pulses

        if longest > MAX_PULSE_NS or value in INVALID_RAW:
            return None
        if value & 0x800000:
            value -= 1 << 24
        return value

    def read_median(self, seconds=1.0, min_samples=3):
        """Mediana de las lecturas válidas obtenidas durante `seconds`."""
        samples = []
        end = monotonic() + seconds
        while monotonic() < end or len(samples) < min_samples:
            raw = self.read_raw()
            if raw is not None:
                samples.append(raw)
            elif monotonic() > end + 5:
                raise TimeoutError("HX711: lecturas inválidas, revisar cableado")
        return median(samples)

    def tare(self, seconds=10.0):
        """Fija el cero con la báscula vacía."""
        self.offset = self.read_median(seconds)

    def weight(self, seconds=1.0):
        """Peso en unidades de calibración: (lectura - offset) / unidad."""
        return (self.read_median(seconds) - self.offset) / self.reference_unit
