from gpiozero import AngularServo, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

SAPO = 13

# Declaración de pines
factory = PiGPIOFactory()
servo_sapo = AngularServo(pin=SAPO, initial_angle=90, pin_factory=factory)

try:
    servo_sapo.max()
    sleep(15)

except KeyboardInterrupt:
    exit(1)

finally:
    servo_sapo.close()
