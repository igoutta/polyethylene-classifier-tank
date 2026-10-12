import os
import tempfile

import pytest

# Pines simulados (con PWM): se fijan antes de que gpiozero se importe
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "mock")
os.environ.setdefault("GPIOZERO_MOCK_PIN_CLASS", "mockpwmpin")
# Nunca escribir estado en el directorio personal durante las pruebas
os.environ["TANK_STATE_DIR"] = tempfile.mkdtemp(prefix="tank-tests-")
os.environ["TANK_LIVE_DIR"] = tempfile.mkdtemp(prefix="tank-tests-live-")

# Después de fijar el entorno: gpiozero lee la fábrica de pines al usarse
from gpiozero import Device

from polyethylene_tank.config import PESO_FILE, TIEMPOS_FILE


@pytest.fixture(autouse=True)
def fast_servos(monkeypatch):
    """Los movimientos de servos esperan segundos; en las pruebas no."""
    monkeypatch.setattr("polyethylene_tank.tank.sleep", lambda _: None)


@pytest.fixture(autouse=True)
def reset_pins():
    """Los pines simulados guardan su estado: se limpian tras cada prueba."""
    yield
    if Device.pin_factory is not None:
        Device.pin_factory.reset()


@pytest.fixture(autouse=True)
def clean_state():
    """Cada prueba empieza sin tiempos guardados ni peso publicado."""
    yield
    TIEMPOS_FILE.unlink(missing_ok=True)
    PESO_FILE.unlink(missing_ok=True)
