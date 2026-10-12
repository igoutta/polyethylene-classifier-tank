"""Pines (numeración J8 de gpiozero) y tiempos del ciclo."""

# Entradas
INICIAR = "J8:37"
PARAR = "J8:35"
FIN_CARRERA = "J8:19"

# Relés de las bombas
RELE_LLENADO = "J8:7"
RELE_CORRIENTE = "J8:11"

# Motor NEMA
NEMA_STEP = "J8:3"
NEMA_DIR = "J8:5"

# Servos (PWM)
SAPO = "J8:33"
TUNEL = "J8:32"

# Tiempos del ciclo (segundos)
TIEMPO_LLENADO_SEC = 15
TIEMPO_LIMPIEZA_SEC = 60
TIEMPO_DESFOGUE_SEC = 15

# Servidor web
HOST = "0.0.0.0"
PORT = 8080
