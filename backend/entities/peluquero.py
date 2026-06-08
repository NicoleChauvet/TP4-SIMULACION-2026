class Peluquero:
    def __init__(self, nombre):
        # Atributos puros de la Entidad
        self.nombre = nombre
        self.estado = "Libre"
        self.cliente_actual = None
        self.fin_atencion = float('inf')

    def ocupar(self, cliente, tiempo_fin_atencion):
        # El peluquero simplemente acata la orden del simulador
        self.estado = "Ocupado"
        self.cliente_actual = cliente
        self.fin_atencion = tiempo_fin_atencion

    def liberar(self): 
        self.estado = "Libre"
        self.cliente_actual = None
        self.fin_atencion = float('inf')

    def __str__(self):
        return self.estado