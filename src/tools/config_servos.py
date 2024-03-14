from gpiozero import AngularServo, Servo
from signal import pause

# from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import warnings

warnings.filterwarnings("ignore")

SAPO = "J8:33"
TUNEL = "J8:32"

# Declaración de pines
# factory = PiGPIOFactory()
servo_sapo = AngularServo(pin=SAPO, initial_angle=0)  # pin_factory=factory)
servo_tunel = Servo(pin=TUNEL, initial_value=0)  # pin_factory=factory)

try:
    while True:
        servo_tunel.detach()
        servo_sapo.min()
        sleep(2)
        servo_sapo.max()
        sleep(2)
        servo_tunel.min()
        sleep(1.7)
        servo_tunel.max()
        sleep(1.1)
        servo_tunel.detach()
except KeyboardInterrupt:
    exit(1)

finally:
    servo_sapo.close()
    servo_tunel.close()
