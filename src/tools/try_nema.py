from gpiozero import PhaseEnableMotor
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

NEMA_STEP = "J8:3"
NEMA_DIR = "J8:5"

factory = PiGPIOFactory()
nema = PhaseEnableMotor(phase=NEMA_DIR, enable=NEMA_STEP, pin_factory=factory)

try:
    nema.forward(speed=0.99)
    sleep(3)
    nema.backward(speed=0.99)
    sleep(2)

except KeyboardInterrupt:
    exit(1)

finally:
    nema.stop()
    nema.close()
