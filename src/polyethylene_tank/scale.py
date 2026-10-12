"""Balanza (HX711) con pantalla LCD I2C. Servicio independiente del tanque.

Usa `hx711-rpi-py` (necesita libhx711: scripts/install-hx711.sh).
Ejecutar: `uv run --extra scale tank-scale`
"""

import logging
from datetime import timedelta

from HX711 import AdvancedHX711, Options, Rate, ReadType
from RPLCD.i2c import CharLCD

from .config import LOG_FORMAT, SCALE_CLOCK, SCALE_DATA, SCALE_REFERENCE_UNIT

log = logging.getLogger(__name__)

LCD_COLUMNS = 16
TARE_SECONDS = 10
READ_SECONDS = 1


def _mostrar(lcd, peso):
    # Se sobrescribe la segunda línea en vez de limpiar: la pantalla no parpadea
    lcd.cursor_pos = (1, 0)
    lcd.write_string(f"{peso:>{LCD_COLUMNS}.1f}")


def _medir(seconds):
    # Tantas muestras como entren en `seconds`, usando la mediana
    return Options(timedelta(seconds=seconds), ReadType.Median)


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    lcd = CharLCD(
        i2c_expander="PCF8574",
        address=0x27,
        port=1,
        cols=LCD_COLUMNS,
        rows=2,
        dotsize=8,
        backlight_enabled=True,
    )
    lcd.clear()
    lcd.write_string("Peso:")
    try:
        # offset 0: el cero se fija con zero() al iniciar. 80 Hz = pin RATE del chip
        with AdvancedHX711(
            SCALE_DATA, SCALE_CLOCK, SCALE_REFERENCE_UNIT, 0, Rate.HZ_80
        ) as hx:
            log.info("Cero en %d s: la báscula debe estar vacía", TARE_SECONDS)
            hx.zero(_medir(TARE_SECONDS))
            log.info("Balanza lista")
            while True:
                peso = float(hx.weight(_medir(READ_SECONDS)))
                log.debug("Peso: %.1f", peso)
                _mostrar(lcd, peso)
    except KeyboardInterrupt:
        log.info("Balanza detenida")
    finally:
        lcd.close(clear=True)


if __name__ == "__main__":
    main()
