#!/usr/bin/python3
from RPLCD.i2c import CharLCD
from HX711 import SimpleHX711, ReadType, Options
from datetime import timedelta

lcd = CharLCD(
    i2c_expander="PCF8574",
    address=0x27,
    port=1,
    cols=16,
    rows=2,
    dotsize=8,
    backlight_enabled=True,
)
lcd.clear()

with SimpleHX711(9, 11, 1, 8388607) as hx:
    hx.zero(Options(timedelta(seconds=5), ReadType.Average))
    try:
        while True:
            # eg. obtain as many samples as possible within 1 second
            m = hx.weight(timedelta(seconds=1))
            lcd.clear()
            lcd.write_string("Peso: ")
            lcd.write_string(str(("0 g", m)[m != 0]))
            print(str(("0 g", m)[m != 0]))
    except KeyboardInterrupt:
        print()
        lcd.close(clear=True)
        exit(1)
