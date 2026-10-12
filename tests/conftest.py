import os

import pytest

# Pines simulados (con PWM): se fijan antes de que gpiozero se importe
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "mock")
os.environ.setdefault("GPIOZERO_MOCK_PIN_CLASS", "mockpwmpin")

# Después de fijar el entorno: gpiozero lee la fábrica de pines al usarse
from gpiozero import Device


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
