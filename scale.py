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
DATA = 9
# 21
CLOCK = 11
# 23
with SimpleHX711(DATA, CLOCK, -7627, 3307908) as hx:
    # hx.setReferenceUnit(-4559) and hx.setOffset(1101338)
    hx.zero(Options(timedelta(seconds=10), ReadType.Average))
    try:
        while True:
            # eg. obtain as many samples as possible within 1 second
            m = hx.weight(Options(timedelta(seconds=2), ReadType.Median))
            lcd.clear()
            lcd.write_string("Peso: \n")
            lcd.write_string(str(("0 g", m)[m >= 0]))
            print(str(("0 g", m)[m != 0]))
            m = 0
    except KeyboardInterrupt:
        print()
        lcd.close(clear=True)
        exit(1)
