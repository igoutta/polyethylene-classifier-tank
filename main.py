from gpiozero import Button
from signal import pause


def start():
    print("Hello!")


def stop():
    print("Parar")


button = Button(2)

button.when_pressed = start

pause()
