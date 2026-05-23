from functions.generador_uniforme import generar_uniforme
from entities.peluquero import Peluquero
from entities.cliente import Cliente


class Simulador:
    def __init__(self, N, X, i, j):
        self.N_dias = N # cantidad de dias a simular
        self.X_tiempo = X # tiempo total a simular en minutos (N dias * 8 horas * 60 minutos)
        self.i_iteraciones = i # cantidad de iteraciones a realizar para cada valor de j
        self.j_minuto = j # minuto a partir del cual se empieza a contar el tiempo de espera de los clientes para calcular el promedio al final de la simulacion

    # congiguraciones del sistema a simular
    self.duracion_dia = 8 * 60 # duracion de un dia en minutos (8 horas * 60 minutos)
    self.tiempo_tolerancia = 30 # tiempo de tolerancia de los clientes en minutos

    #instanciamos las entidades
    self.aprendiz = Peluquero("Aprendiz", 20, 30)
    self.veterano_a = Peluquero("Veterano A", 11, 13)
    self.veterano_b = Peluquero("Veterano B", 12, 18)
    self.peluqueros = [self.aprendiz, self.veterano_a, self.veterano_b]

    # relojes y contadores
    self.reloj = 0.0 # reloj global de la simulacion
    self.reloj_dia = 0.0 # reloj que se reinicia cada dia para controlar la llegada de los clientes
    self.dia_actual = 1 # dia actual de la simulacion
    self.iteracion_actual = 1 # iteracion actual de la simulacion
    self.id_cliente = 1 # id del cliente que se va a crear, se incrementa cada vez que se crea un cliente

    # estados de la cola y los eventos
    self.cola = [] # cola de clientes esperando para ser atendidos
    self.total_abandonos = 0 # contador de clientes que abandonan la cola por superar su tiempo de tolerancia
    self.prox_llegada = 0.0 # tiempo en el que se espera que llegue el proximo cliente
    self.prox_cierre = self.duracion_dia # tiempo en el que se espera que cierre el dia, se reinicia cada dia

    self.iteraciones_mostradas = 0 # contador de iteraciones mostradas en la tabla de eventos, se incrementa cada vez que se muestra una iteracion
    self.evento_actual = "inicializacion de la simulacion" 
    self.rnd_str = "" # string para mostrar el numero aleatorio generado en cada evento

    def inicializar_dia(self):
        # reiniciamos los relojes y contadores para el nuevo dia
        self.reloj_dia = 0.0
        self.id_cliente = 1
        self.cola.clear()
        
        for p in self.peluqueros:
            p.liberar()
            
        rnd, t_lleg = generar_uniforme(2, 12)
        self.prox_llegada = t_lleg
        self.prox_cierre = self.duracion_dia

    def obtener_prox_abandono(self):
        # obtenemos el tiempo en el que se espera que abandone la cola el proximo cliente, si es que hay clientes en la cola
        if not self.cola:
            return float('inf')
        return min(cliente.tiempo_tolerancia for cliente in self.cola)