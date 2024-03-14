from gpiozero import AngularServo, Servo

# from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

SAPO = 13
TUNEL = "J8:32"

# Declaración de pines
# factory = PiGPIOFactory()
servo_sapo = AngularServo(pin=SAPO, initial_angle=0)  # pin_factory=factory)
servo_tunel = Servo(pin=TUNEL, initial_value=0)  # pin_factory=factory)

try:
    servo_tunel.min()
    sleep(1.1)
    servo_tunel.max()
    sleep(0.95)

except KeyboardInterrupt:
    exit(1)

finally:
    servo_sapo.close()
    servo_tunel.close()
