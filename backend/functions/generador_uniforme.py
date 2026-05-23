import random

def generar_uniforme(a, b):
    rnd = random.random() # genera un numero aleatorio entre 0 y 1
    tiempo = a + rnd * (b - a) # transforma el numero aleatorio a un numero entre a y b
    return round (rnd, 4), round (tiempo, 4)

