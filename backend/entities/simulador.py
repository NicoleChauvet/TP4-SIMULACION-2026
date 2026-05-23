import random
from functions.generador_uniforme import generar_uniforme
from functions.generador_csv import inicializar_csv, agregar_fila_csv
from entities.peluquero import Peluquero
from entities.cliente import Cliente

class Simulador:
    def __init__(self, N, X, i, j):
        self.N_dias = N # cantidad de dias a simular
        self.X_tiempo = X # tiempo total máximo global de simulación (minutos)
        self.i_iteraciones = i # cantidad de iteraciones consecutivas a mostrar
        self.j_minuto = j # minuto absoluto a partir del cual se empieza a mostrar

        # configuraciones del sistema a simular
        self.duracion_dia = 480 
        self.tiempo_tolerancia = 30 

        # instanciar entidades
        self.aprendiz = Peluquero("Aprendiz", 20, 30)
        self.veterano_a = Peluquero("Veterano A", 11, 13)
        self.veterano_b = Peluquero("Veterano B", 12, 18)
        self.peluqueros = [self.aprendiz, self.veterano_a, self.veterano_b]

        # relojes y contadores
        self.reloj = 0.0 # reloj global acumulado de la simulación
        self.reloj_dia = 0.0 # reloj de tiempo interno del día actual
        self.dia_actual = 1 
        self.iteracion_actual = 1 
        self.id_cliente = 1 

        # estados de la cola y los eventos
        self.cola = [] 
        self.total_abandonos = 0 
        self.prox_llegada = 0.0 
        self.prox_cierre = self.duracion_dia 

        self.iteraciones_mostradas = 0 
        self.evento_actual = "Inicializacion" 
        self.rnd_str = "-" 
        
        # Nombre del archivo donde se guardará todo
        self.archivo_csv = "Vector_Estados_Peluqueria.csv"

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

    def obtener_prox_abandono(self):
        if not self.cola:
            return float('inf')
        return min(cliente.hora_abandono for cliente in self.cola)
    
    def ejecutar(self):
        # 1. Inicializar el almacenamiento físico de la simulación
        inicializar_csv(self.archivo_csv)
        self.inicializar_dia()
        
        # Guardar la fila inicial (Fila 0 o Inicialización)
        self.registrar_fila()

        # ================== BUCLE DE EVENTOS ==================
        while self.dia_actual <= self.N_dias and self.reloj <= self.X_tiempo:
            reloj_anterior = self.reloj_dia
            
            # Buscar el tiempo del próximo abandono programado en cola
            prox_abandono = self.obtener_prox_abandono()
            
            # Mapear el cuadro general de tiempos de eventos
            eventos = {
                'Llegada Cliente': self.prox_llegada,
                'Fin Atencion Ap': self.aprendiz.fin_atencion,
                'Fin Atencion VA': self.veterano_a.fin_atencion,
                'Fin Atencion VB': self.veterano_b.fin_atencion,
                'Abandono': prox_abandono,
                'Cierre Recepcion': self.prox_cierre
            }
            
            # Control de fin de jornada diaria
            if self.reloj_dia >= self.duracion_dia and len(self.cola) == 0 and all(p.estado == 'Libre' for p in self.peluqueros):
                self.evento_actual = 'Fin de Dia'
            else:
                self.evento_actual = min(eventos, key=eventos.get)
                self.reloj_dia = eventos[self.evento_actual]
                # Avanzamos el reloj global basándonos en la diferencia del salto temporal
                self.reloj += (self.reloj_dia - reloj_anterior)

            self.rnd_str = "-"

            # ================== LÓGICA ESPECÍFICA DE PROCESAMIENTO ==================
            if self.evento_actual == 'Llegada Cliente':
                if self.reloj_dia < self.duracion_dia:
                    rnd_lleg, t_lleg = generar_uniforme(2, 12)
                    self.prox_llegada = self.reloj_dia + t_lleg
                    self.rnd_str = str(rnd_lleg)
                
                nuevo_cliente = Cliente(self.id_cliente, self.reloj_dia, self.tiempo_tolerancia)
                self.id_cliente += 1
                
                # Buscar el peluquero correspondiente según su preferencia instanciada
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
                # Buscamos quién de la cola alcanzó su hora máxima cronológica en este minuto
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

            # ================== DISPARADOR DE REGISTRO CSV (Filtro i, j) ==================
            es_ultima_fila = (self.dia_actual > self.N_dias) or (self.reloj > self.X_tiempo)
            
            if (self.reloj >= self.j_minuto and self.iteraciones_mostradas < self.i_iteraciones) or es_ultima_fila:
                self.registrar_fila()
                if not es_ultima_fila:
                    self.iteraciones_mostradas += 1
                    
            self.iteracion_actual += 1

        print(f"\n Simulación guardada con éxito en el archivo '{self.archivo_csv}'")

    def procesar_fin_atencion(self, peluquero):
        # Buscamos en la cola única bajo lógica FIFO al primero que prefiera este servidor
        siguiente_cliente = next((c for c in self.cola if c.preferencia == peluquero.nombre), None)
        if siguiente_cliente:
            self.cola.remove(siguiente_cliente)
            peluquero.ocupar(siguiente_cliente, self.reloj_dia)
        else:
            peluquero.liberar()

    def registrar_fila(self):
        # Formatear infinitos para evitar ruido visual en las planillas Excel
        p_lleg = round(self.prox_llegada, 2) if self.prox_llegada != float('inf') else "-"
        f_ap = round(self.aprendiz.fin_atencion, 2) if self.aprendiz.fin_atencion != float('inf') else "-"
        f_va = round(self.veterano_a.fin_atencion, 2) if self.veterano_a.fin_atencion != float('inf') else "-"
        f_vb = round(self.veterano_b.fin_atencion, 2) if self.veterano_b.fin_atencion != float('inf') else "-"
        
        # Estructuramos el arreglo lineal de datos ordenados según las columnas declaradas
        datos_fila = [
            self.iteracion_actual,
            self.dia_actual if self.evento_actual != "Fin de Dia" else self.dia_actual - 1,
            round(self.reloj, 2),
            round(self.reloj_dia, 2),
            self.evento_actual,
            self.rnd_str,
            "-" if self.evento_actual != "Llegada Cliente" else "Calculado", # TEL temporal
            p_lleg,
            "-" if self.evento_actual != "Llegada Cliente" else "Calculado", # RND preferencia temporal
            "-" if self.evento_actual != "Llegada Cliente" else "Calculado", # preferencia temporal
            str(self.aprendiz), f_ap,
            str(self.veterano_a), f_va,
            str(self.veterano_b), f_vb,
            len(self.cola),
            self.total_abandonos
        ]
        
        # Llamamos a nuestro módulo independiente de persistencia
        agregar_fila_csv(self.archivo_csv, datos_fila)