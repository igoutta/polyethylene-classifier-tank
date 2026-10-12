"""Balanza (HX711) con pantalla LCD I2C. Servicio independiente del tanque.

Ejecutar: `uv run --extra pi --extra scale tank-scale`
"""

from RPLCD.i2c import CharLCD

from .config import SCALE_CLOCK, SCALE_DATA, SCALE_REFERENCE_UNIT
from .hx711 import HX711

LCD_COLUMNS = 16


def _mostrar(lcd, peso):
    # Se sobrescribe la segunda línea en vez de limpiar: la pantalla no parpadea
    lcd.cursor_pos = (1, 0)
    lcd.write_string(f"{peso:>{LCD_COLUMNS}.1f}")


def main():
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
        with HX711.from_gpio(SCALE_DATA, SCALE_CLOCK) as hx:
            hx.reference_unit = SCALE_REFERENCE_UNIT
            hx.tare(seconds=10)
            while True:
                peso = hx.weight(seconds=1)
                print(peso)
                _mostrar(lcd, peso)
    except KeyboardInterrupt:
        print()
    finally:
        lcd.close(clear=True)


if __name__ == "__main__":
    main()
