# Implementación del algoritmo para el uso del tanque con polyetileno

## 1. Identificación del algoritmo

Para que un algoritmo escrito en Python en la Raspberry Pi funcione adecuadamente, es necesario indicar primeramente el ambiente en cual se ejecuta. En este caso, se utiliza *#!/usr/bin/python3*, que contiene el sitio por defecto donde se encuentra el ejecutor del algoritmo.

## 2. Importación de bibliotecas

Las palabras reversadas *from* e *import* indican la importación de librerías/bibliotecas que contienen elementos necesarios para crear el algoritmo.

Principalmente, se usa signal para mantener en bucle.

## 3. Declaración de pines

Con el fin de controlar y leer tanto actuadores como sensores, es necesario asignar el uso de los pines fisicos a nuestras variables según su uso. En este caso, la mayoría usa lógica binaria, es decir escoge entre dos valores, sean estos 1 o 0, True or False, 5V o 0V, equivalentes entre sí mas distintos según el marco en cuestión (matemático, computacional y eléctrico). El resto de pines a usar varia en un espectro limitado conocido como PWM, que para nuestra facilidad es cualquier valor real entre -1 y 1, que son parte de las condiciones iniciales.

Los pines se nombran de varias formas, en nuestro caso se ha elegido la más fácil, que es la ascendente. Para esto se llama al pin con el prefijo "J8:*x*" donde *x* el numero del pin, que van del 1 al 40.

## 4. Inicialización de variables

Las variables que rigen el sistema algorítmico necesitan ser iniciadas y cargadas a la memoria de la computadora. A través de su nombramiento en Python, éstas se cargan durante la ejecución.

Se pueden diferenciar tres grandes grupos: entradas, salidas y tiempos de ejecución.

## 5. Declaración de funciones

Fragmentar el algoritmo en partes que tienen una finalidad, ayuda a la legibilidad y facilita de mantenimiento de éste. En este caso, gracias a que la secuencia está bien delimitada y no existen condiciones de carrera, sólo son tres funciones: la principal, una auxiliar para crear retraso en el script, y la de parada.

La función principal, llamada main se divide en tres grandes bloques de secuencias: preparación, desfogue y parada.

- La fase de preparación se encarga de dos cosas: prender la bomba y esperar que el sensor de final de carrera detecte que la piscina está llena. Además, guarda el tiempo para usar en el desfogue.
- La fase de desfogue es la que utiliza los motores para limpiar el tanque de los restos de polietilenos y se abre el tubo de escape de agua.
- En la fase de parada el sistema apaga el motor de limpieza y cierra la piscina, tapando en tubo de escape y luego quitando los restos de dicho tubo.

> wait_for_active() sirve para esperar indefinidamente que el sensor de fin de carrera se ponga en estado True.

La función auxiliar custom_sleep sirve para esperar mientras se cumplan dos condiciones:

1. Que el botón de parada no este presionado.
2. Que el tiempo transcurrido (diferencia entre final e inicial) sea menor al tiempo que la persona para como paramétro de entrada.

> monotonic() es un contador de tiempo que no retrocede y no se pueden parar mediante programación. Perfecto para este proyecto.

La función de parada simplemente es una secuencia para finalizar el script

## 6. Seguridad en la ejecución del algoritmo

La función safe_exit, la creación de dos señales, son prácticas de seguridad a la hora de ejecutar el algoritmo. El primero simplemente ayuda a terminar el script con un aviso, por eso el valor 1. Este se lo asigna a dos señales.

El bloque try, implementa la ejecución del código o que realizar si ocurre algún error o excepción. En nuestro caso, siempre que pase algo, se parar los actuadores y descarga las variables del pines, dejandolos libres.

## 7. Lógica del algoritmo

Basicamente consiste en asigna como evento las funciones segun el boton, la función main al boton de activar y la de stop al boton de parar. Esto crea un vinculo que sucede al presionar el boton, que da paso a ejecutar dicha orden.

> pause() es el comando para mantener corriendo indefinidamente el algoritmo, mientras que deja activar los botones.

## Auto Iniciar el script

Crear un servicio con `sudo nano /etc/systemd/system/polyethylene-classifier-tank.service`

```properties
[Unit]
Description=Polyethylene Classifier Tank Service
After=syslog.target

[Service]
Type=simple
User=ga
WorkingDirectory=/home/ga/polyethylene-classifier-tank
ExecStartPre=sudo pigpiod
ExecStart=/usr/bin/python3 -u main.py
StandardOutput=syslog
StandardError=syslog
Restart=always
TimeoutStartSec=10
RestartSec=10

[Install]
WantedBy=multi-user.target

```

```properties
[Unit]
Description=Polyethylene Scale Service
After=syslog.target

[Service]
Type=simple
User=ga
WorkingDirectory=/home/ga/polyethylene-classifier-tank
ExecStart=/home/ga/polyethylene-classifier-tank/env/bin/python -u scale.py
StandardOutput=syslog
StandardError=syslog
Restart=always
TimeoutStartSec=10
RestartSec=10

[Install]
WantedBy=multi-user.target

```

## Instalación de otras dependencias para I2C y HX711

`sudo apt update` && `sudo apt upgrade`

`sudo raspi-config`

Once you’ve opened the Raspberry Pi Configuration tool, go to the Interfacing Options menu and choose I2C. Then, enable I2C by selecting ‘Yes’ and hitting Enter. Finally, exit the raspi-config tool by selecting ‘Finish.’

`sudo reboot`

`sudo apt install -y i2c-tools python3-smbus`

`lsmod | grep i2c_`

`sudo reboot`

`i2cdetect -y 1`

### Ambiente virtual

Dentro de la raíz del repositorio, para crear el entorno virtual: `python3 -m venv env`
Por si acaso no se hace de antemano, ignorar el hecho de guardar el ambiente virtual con: `echo ‘env' > .gitignore`
Para activarlo: `source env/bin/activate` y para desactivarlo: `deactivate`
Para guardar las bibliotecas usar: `pip freeze > requirements.txt` y para instalarlas: `pip install -r requeriments.txt`

### Librerias o Bibliotecas

`pip3 install RPLCD smbus2`

### [HX711](https://github.com/endail/hx711-rpi-py)

`sudo apt install -y liblgpio-dev`

```sh
cd $HOME && git clone --depth=1 https://github.com/endail/hx711
cd hx711
make |& tee build.log
sudo make install
sudo ldconfig
```

`pip install --upgrade hx711-rpi-py`
