import random
from functions.generador_uniforme import generar_uniforme
from entities.peluquero import Peluquero
from entities.cliente import Cliente

COLUMNAS = [
    "Iteracion", "Dia", "Reloj_Absoluto", "Reloj_Dia", "Evento",
    "RND_Llegada", "T_Llegada", "Prox_Llegada",
    "RND_Preferencia", "Preferencia_Cliente",
    "Aprendiz_Estado", "Aprendiz_Fin",
    "VetA_Estado", "VetA_Fin",
    "VetB_Estado", "VetB_Fin",
    "Tamaño_Cola", "Total_Abandonos"
]

class Simulador:
    def __init__(self, N, X, i, j):
        self.N_dias = N
        self.X_tiempo = X
        self.i_iteraciones = i
        self.j_minuto = j

        self.duracion_dia = 480
        self.tiempo_tolerancia = 30

        self.aprendiz = Peluquero("Aprendiz", 20, 30)
        self.veterano_a = Peluquero("Veterano A", 11, 13)
        self.veterano_b = Peluquero("Veterano B", 12, 18)
        self.peluqueros = [self.aprendiz, self.veterano_a, self.veterano_b]

        self.reloj = 0.0
        self.reloj_dia = 0.0
        self.dia_actual = 1
        self.iteracion_actual = 1
        self.id_cliente = 1

        self.cola = []
        self.total_abandonos = 0
        self.prox_llegada = 0.0
        self.prox_cierre = self.duracion_dia

        self.iteraciones_mostradas = 0
        self.evento_actual = "Inicializacion"
        self.rnd_str = "-"
        self.t_llegada_str = "-"
        self.rnd_pref_str = "-"
        self.pref_str = "-"

        # En memoria en lugar de CSV
        self.filas = []

    def inicializar_dia(self):
        self.reloj_dia = 0.0
        self.id_cliente = 1
        self.cola.clear()

        for p in self.peluqueros:
            p.liberar()

        rnd, t_lleg = generar_uniforme(2, 12)
        self.prox_llegada = t_lleg
        self.prox_cierre = self.duracion_dia
        self.rnd_str = str(rnd)
        self.t_llegada_str = "-"
        self.rnd_pref_str = "-"
        self.pref_str = "-"

    def obtener_prox_abandono(self):
        if not self.cola:
            return float('inf')
        return min(cliente.hora_abandono for cliente in self.cola)

    def ejecutar(self):
        self.inicializar_dia()
        self.registrar_fila()

        while self.dia_actual <= self.N_dias and self.reloj <= self.X_tiempo:
            reloj_anterior = self.reloj_dia

            prox_abandono = self.obtener_prox_abandono()

            eventos = {
                'Llegada Cliente': self.prox_llegada,
                'Fin Atencion Ap': self.aprendiz.fin_atencion,
                'Fin Atencion VA': self.veterano_a.fin_atencion,
                'Fin Atencion VB': self.veterano_b.fin_atencion,
                'Abandono': prox_abandono,
                'Cierre Recepcion': self.prox_cierre
            }

            if self.reloj_dia >= self.duracion_dia and len(self.cola) == 0 and all(p.estado == 'Libre' for p in self.peluqueros):
                self.evento_actual = 'Fin de Dia'
            else:
                self.evento_actual = min(eventos, key=eventos.get)
                self.reloj_dia = eventos[self.evento_actual]
                self.reloj += (self.reloj_dia - reloj_anterior)

            self.rnd_str = "-"
            self.t_llegada_str = "-"
            self.rnd_pref_str = "-"
            self.pref_str = "-"

            if self.evento_actual == 'Llegada Cliente':
                if self.reloj_dia < self.duracion_dia:
                    rnd_lleg, t_lleg = generar_uniforme(2, 12)
                    self.prox_llegada = self.reloj_dia + t_lleg
                    self.rnd_str = str(rnd_lleg)
                    self.t_llegada_str = str(t_lleg)

                nuevo_cliente = Cliente(self.id_cliente, self.reloj_dia, self.tiempo_tolerancia)
                self.id_cliente += 1

                self.rnd_pref_str = str(nuevo_cliente.rnd_preferencia)
                self.pref_str = nuevo_cliente.preferencia

                peluquero_objetivo = None
                if nuevo_cliente.preferencia == "Aprendiz": peluquero_objetivo = self.aprendiz
                elif nuevo_cliente.preferencia == "Veterano A": peluquero_objetivo = self.veterano_a
                elif nuevo_cliente.preferencia == "Veterano B": peluquero_objetivo = self.veterano_b

                if peluquero_objetivo.estado == "Libre":
                    peluquero_objetivo.ocupar(nuevo_cliente, self.reloj_dia)
                else:
                    self.cola.append(nuevo_cliente)

            elif self.evento_actual == 'Fin Atencion Ap':
                self.procesar_fin_atencion(self.aprendiz)

            elif self.evento_actual == 'Fin Atencion VA':
                self.procesar_fin_atencion(self.veterano_a)

            elif self.evento_actual == 'Fin Atencion VB':
                self.procesar_fin_atencion(self.veterano_b)

            elif self.evento_actual == 'Abandono':
                cliente_retirado = next((c for c in self.cola if c.hora_abandono == self.reloj_dia), None)
                if cliente_retirado:
                    self.cola.remove(cliente_retirado)
                    self.total_abandonos += 1

            elif self.evento_actual == 'Cierre Recepcion':
                self.prox_llegada = float('inf')
                self.prox_cierre = float('inf')

            elif self.evento_actual == 'Fin de Dia':
                self.dia_actual += 1
                if self.dia_actual <= self.N_dias:
                    self.inicializar_dia()

            es_ultima_fila = (self.dia_actual > self.N_dias) or (self.reloj > self.X_tiempo)

            if (self.reloj >= self.j_minuto and self.iteraciones_mostradas < self.i_iteraciones) or es_ultima_fila:
                self.registrar_fila()
                if not es_ultima_fila:
                    self.iteraciones_mostradas += 1

            self.iteracion_actual += 1

        return self.filas, COLUMNAS

    def procesar_fin_atencion(self, peluquero):
        siguiente_cliente = next((c for c in self.cola if c.preferencia == peluquero.nombre), None)
        if siguiente_cliente:
            self.cola.remove(siguiente_cliente)
            peluquero.ocupar(siguiente_cliente, self.reloj_dia)
        else:
            peluquero.liberar()

    def registrar_fila(self):
        p_lleg = round(self.prox_llegada, 2) if self.prox_llegada != float('inf') else "-"
        f_ap = round(self.aprendiz.fin_atencion, 2) if self.aprendiz.fin_atencion != float('inf') else "-"
        f_va = round(self.veterano_a.fin_atencion, 2) if self.veterano_a.fin_atencion != float('inf') else "-"
        f_vb = round(self.veterano_b.fin_atencion, 2) if self.veterano_b.fin_atencion != float('inf') else "-"

        fila = [
            self.iteracion_actual,
            self.dia_actual if self.evento_actual != "Fin de Dia" else self.dia_actual - 1,
            round(self.reloj, 2),
            round(self.reloj_dia, 2),
            self.evento_actual,
            self.rnd_str,
            self.t_llegada_str,
            p_lleg,
            self.rnd_pref_str,
            self.pref_str,
            str(self.aprendiz), f_ap,
            str(self.veterano_a), f_va,
            str(self.veterano_b), f_vb,
            len(self.cola),
            self.total_abandonos
        ]

        self.filas.append(fila)
