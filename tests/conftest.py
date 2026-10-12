import os

import pytest

# Pines simulados (con PWM): se fijan antes de que gpiozero se importe
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "mock")
os.environ.setdefault("GPIOZERO_MOCK_PIN_CLASS", "mockpwmpin")


@pytest.fixture(autouse=True)
def fast_servos(monkeypatch):
    """Los movimientos de servos esperan segundos; en las pruebas no."""
    monkeypatch.setattr("polyethylene_tank.tank.sleep", lambda _: None)
