import random

class Cliente:
    def __init__(self, id_cliente, reloj, tiempo_tolerancia):
        self.id_cliente = id_cliente
        self.reloj = reloj
        self.tiempo_tolerancia = tiempo_tolerancia

        # cuando se crea un cliente se define la preferencia del mismo
        rnd_preferencia = round(random.random(),4)
        if rnd_preferencia < 0.15:
            self.preferencia = "Aprendiz"
        elif rnd_preferencia < 0.60:
            self.preferencia = "Veterano A"
        else:
            self.preferencia = "Veterano B"