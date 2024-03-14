from gpiozero import PhaseEnableMotor
from time import sleep

NEMA_STEP = "J8:3"
NEMA_DIR = "J8:5"

nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP)

try:
    while True:
        nema.forward(speed=0.9)  # ni 0.999 ni 0.95 ni 1
        sleep(45)
        nema.reverse()
        sleep(45)

except KeyboardInterrupt:
    exit(1)

finally:
    nema.stop()
    sleep(1)
    nema.close()
