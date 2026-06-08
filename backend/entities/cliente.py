class Cliente:
    def __init__(self, id_cliente, preferencia):
        self.id_cliente = id_cliente
        self.preferencia = preferencia
        self.hora_llegada_cola = None
        self.estado = ""