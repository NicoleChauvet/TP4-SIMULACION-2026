import random

class Cliente:
    def __init__(self, id_cliente, reloj, tiempo_tolerancia):
        self.id_cliente = id_cliente
        self.reloj = reloj
        self.hora_abandono = reloj + tiempo_tolerancia

        # Cuando se crea un cliente se define la preferencia del mismo
        self.rnd_preferencia = round(random.random(),4)
        if self.rnd_preferencia < 0.15:
            self.preferencia = "Aprendiz"
        elif self.rnd_preferencia < 0.60:
            self.preferencia = "Veterano A"
        else:
            self.preferencia = "Veterano B"