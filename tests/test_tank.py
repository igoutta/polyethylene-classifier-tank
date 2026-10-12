import time

import pytest

from polyethylene_tank import tank as tank_module
from polyethylene_tank.settings import Tiempos
from polyethylene_tank.tank import Tank


@pytest.fixture
def tank(monkeypatch):
    monkeypatch.setattr(tank_module, "PAUSA_MOTOR_SEC", 0.01)
    tank = Tank(tiempos=Tiempos(llenado=0.2, limpieza=0.2, desfogue=0.2))
    yield tank
    # Con el sensor activo, gpiozero tarda ~1 s en cerrar el Button
    tank.sensor_limite.pin.drive_low()
    tank.close()


def esperar(condicion, timeout=3.0):
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if condicion():
            return True
        time.sleep(0.01)
    return False


def bombas_apagadas(tank):
    return not (
        tank.bomba_llenado.is_lit
        or tank.bomba_corriente.is_lit
        or tank.motor_nema.is_active
    )


def tanque_lleno(tank):
    tank.sensor_limite.pin.drive_high()


def test_fill_timeout_stops_with_error(tank):
    tank.start()
    assert esperar(lambda: not tank.running)
    assert "no se llenó" in tank.error
    assert tank.step == "Detenido por error"
    assert bombas_apagadas(tank)


def test_full_tank_moves_on_to_classifying(tank):
    tanque_lleno(tank)
    tank.tiempos = Tiempos(llenado=0.2, limpieza=30, desfogue=0.2)
    tank.start()
    assert esperar(lambda: tank.step == "Clasificando")
    assert tank.bomba_corriente.is_lit
    assert not tank.bomba_llenado.is_lit


def test_stop_cuts_pumps_without_waiting_for_the_stage(tank):
    tanque_lleno(tank)
    tank.tiempos = Tiempos(llenado=0.2, limpieza=30, desfogue=0.2)
    tank.start()
    assert esperar(lambda: tank.step == "Clasificando")
    inicio = time.monotonic()
    tank.stop()
    assert time.monotonic() - inicio < 1
    assert bombas_apagadas(tank)
    assert tank.step == "Detenido"
    assert tank.error is None


def test_unexpected_error_is_reported_and_stops(tank, monkeypatch):
    def falla():
        raise RuntimeError("fallo simulado")

    tanque_lleno(tank)
    monkeypatch.setattr(tank, "_clasificar", falla)
    tank.start()
    assert esperar(lambda: not tank.running)
    assert tank.error == "fallo simulado"
    assert bombas_apagadas(tank)


def test_start_clears_previous_error(tank):
    tank.start()
    assert esperar(lambda: not tank.running)
    assert tank.error
    tanque_lleno(tank)
    tank.start()
    assert tank.error is None
