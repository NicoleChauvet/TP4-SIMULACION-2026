import random
from functions.generador_uniforme import generar_uniforme

class Peluquero:
    def __init__(self, nombre, a, b):
        self.nombre = nombre
        self.a = a # limite inferior de la distribucion uniforme para el tiempo de corte
        self.b = b # limite superior de la distribucion uniforme para el tiempo de corte
        self.estado = "Libre" # puede ser "Libre" o "Ocupado"
        self.cliente_actual = None # cliente que esta atendiendo actualmente, si es que esta ocupado
        self.fin_atencion = float('inf') # tiempo en el que se espera que termine de atender al cliente actual, si es que esta ocupado

        # metodos del peluquero

        def ocupar(self, cliente, reloj):
            self.estado = "Ocupado"
            self.cliente_actual = cliente
            # el tiempo de atencion se determina al azar con una distribucion uniforme entre a y b
            rnd, tiempo = generar_uniforme(self.a, self.b) # agrego el rnd para que se pueda mostrar en la tabla de eventos y que no se pierda esa informacion
            self.fin_atencion = reloj + tiempo

        def liberar(self): 
            self.estado = "Libre"
            self.cliente_actual = None
            self.fin_atencion = float('inf')

        def __str__(self):
            # nos devuelve string con el estado del peluquero
            if self.estado == "Libre":
                return f"Peluquero {self.nombre}: {self.estado}"
            else:
                return f"Peluquero {self.nombre}: {self.estado} atendiendo al cliente {self.cliente_actual.id_cliente} hasta el tiempo {self.fin_atencion:.2f}"
