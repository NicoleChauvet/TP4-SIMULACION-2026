import random
from entities.peluquero import Peluquero
from entities.cliente import Cliente

# Mapa estricto de columnas base
COLUMNAS = [
    "Fila", "Día", "Reloj Día", "Reloj Absoluto", "Evento", "Número de Cliente",
    "RND Llegada", "Tiempo Llegada", "Próxima Llegada",
    "RND Asignación", "Peluquero Asignado",
    "Estado Aprendiz", "Cliente Aprendiz", "Próx Fin Aprendiz", "Cola Aprendiz",
    "Estado Veterano A", "Cliente Vet A", "Próx Fin Vet A", "Cola Veterano A",
    "Estado Veterano B", "Cliente Vet B", "Próx Fin Vet B", "Cola Veterano B",
    "% Tiempo Libre Aprendiz", "Máximo de Sillas", "Prob cola mayor a 3 en cierre"
]

MAPA_SIGLAS = {
    "Siendo Atendido por Aprendiz": "SAA",
    "Siendo Atendido por Veterano A": "SAVA",
    "Siendo Atendido por Veterano B": "SAVB",
    "En Cola Aprendiz": "ECA",
    "En Cola Veterano A": "ECVA",
    "En Cola Veterano B": "ECVB"
}

class Simulador:
    def __init__(self, X, i, j, params):
        self.tiempo_maximo_simulacion = X
        self.cantidad_iteraciones_mostrar = i
        self.minuto_inicio_mostrar = j

        self.llegada_a = params.get('lleg_a', 2.0)
        self.llegada_b = params.get('lleg_b', 12.0)
        self.ap_a = params.get('ap_a', 20.0)
        self.ap_b = params.get('ap_b', 30.0)
        self.va_a = params.get('va_a', 11.0)
        self.va_b = params.get('va_b', 13.0)
        self.vb_a = params.get('vb_a', 12.0)
        self.vb_b = params.get('vb_b', 18.0)
        
        self.prob_aprendiz = params.get('prob_ap', 15.0) / 100.0
        self.prob_vet_a = params.get('prob_va', 45.0) / 100.0

        self.duracion_jornada = 480.0
        self.tolerancia_espera = 30.0

        self.aprendiz = Peluquero("Aprendiz")
        self.veterano_a = Peluquero("Veterano A")
        self.veterano_b = Peluquero("Veterano B")
        self.peluqueros = [self.aprendiz, self.veterano_a, self.veterano_b]
        
        self.colas = {"Aprendiz": [], "Veterano A": [], "Veterano B": []}

        self.reloj_dia = 0.0
        self.reloj_absoluto = 0.0
        self.dia_actual = 1
        self.iteracion_actual = 1
        self.id_cliente_global = 1

        self.acumulador_tiempo_libre_aprendiz = 0.0
        self.maximo_sillas_usadas = 0
        self.dias_con_cola_larga = 0
        self.cierres_totales = 0

        self.proxima_llegada = 0.0
        self.proximo_cierre = self.duracion_jornada
        self.evento_actual = "Inicio de Día"
        
        self.rnd_llegada_actual = None
        self.tiempo_llegada_actual = None
        self.rnd_preferencia_actual = None
        self.preferencia_actual = None
        self.nro_cliente_actual = "-"

        self.filas_a_mostrar = []
        self.contador_filas_mostradas = 0

    def ejecutar(self):
        self.inicializar_dia()
        self.evaluar_guardado_fila()
        self.iteracion_actual += 1
        self.limpiar_variables_de_fila()

        while self.reloj_absoluto <= self.tiempo_maximo_simulacion and self.iteracion_actual <= 100000:
            reloj_previo = self.reloj_dia

            eventos = {
                'Llegada Cliente': self.proxima_llegada,
                'Fin Atencion Aprendiz': self.aprendiz.fin_atencion,
                'Fin Atencion Veterano A': self.veterano_a.fin_atencion,
                'Fin Atencion Veterano B': self.veterano_b.fin_atencion,
                'Abandono': self.obtener_proximo_abandono(),
                'Cierre Recepcion': self.proximo_cierre
            }

            tiempo_minimo = min(eventos.values())
            total_en_colas = sum(len(c) for c in self.colas.values())
            todos_libres = all(p.estado == 'Libre' for p in self.peluqueros)

            if tiempo_minimo == float('inf') or (self.reloj_dia >= self.duracion_jornada and total_en_colas == 0 and todos_libres):
                proximo_evento = 'Cierre Peluquería'
                avance_reloj = 0
            else:
                proximo_evento = min(eventos, key=eventos.get)
                avance_reloj = tiempo_minimo - reloj_previo

            if self.reloj_absoluto + avance_reloj > self.tiempo_maximo_simulacion:
                avance_restante = self.tiempo_maximo_simulacion - self.reloj_absoluto
                self.reloj_absoluto += avance_restante
                if self.aprendiz.estado == "Libre":
                    self.acumulador_tiempo_libre_aprendiz += avance_restante
                self.evaluar_guardado_fila(forzar_guardado=True)
                break

            self.evento_actual = proximo_evento
            if self.evento_actual != 'Cierre Peluquería':
                self.reloj_dia = tiempo_minimo
            
            self.reloj_absoluto += avance_reloj
            if self.aprendiz.estado == "Libre":
                self.acumulador_tiempo_libre_aprendiz += avance_reloj

            self.nro_cliente_actual = "-"

            if self.evento_actual == 'Llegada Cliente':
                if self.reloj_dia < self.duracion_jornada:
                    rnd_llegada = random.random() 
                    tiempo_llegada = self.llegada_a + rnd_llegada * (self.llegada_b - self.llegada_a)
                    self.proxima_llegada = self.reloj_dia + tiempo_llegada
                    self.rnd_llegada_actual = rnd_llegada
                    self.tiempo_llegada_actual = tiempo_llegada
                else:
                    self.proxima_llegada = float('inf')

                rnd_preferencia = random.random()
                if rnd_preferencia < self.prob_aprendiz:
                    preferencia = "Aprendiz"
                elif rnd_preferencia < (self.prob_aprendiz + self.prob_vet_a):
                    preferencia = "Veterano A"
                else:
                    preferencia = "Veterano B"

                nuevo_cliente = Cliente(self.id_cliente_global, preferencia)
                self.id_cliente_global += 1
                self.rnd_preferencia_actual = rnd_preferencia
                self.preferencia_actual = preferencia

                peluquero_asignado = next(p for p in self.peluqueros if p.nombre == preferencia)
                
                if peluquero_asignado.estado == "Libre":
                    self.iniciar_atencion(peluquero_asignado, nuevo_cliente)
                else:
                    nuevo_cliente.estado = f"En Cola {preferencia}"
                    nuevo_cliente.hora_llegada_cola = self.reloj_dia
                    self.colas[preferencia].append(nuevo_cliente) 
                    self.maximo_sillas_usadas = max(self.maximo_sillas_usadas, sum(len(c) for c in self.colas.values()))

                self.nro_cliente_actual = nuevo_cliente.id_cliente

            elif self.evento_actual.startswith('Fin Atencion'):
                nombre_peluquero = self.evento_actual.replace('Fin Atencion ', '')
                peluquero_terminado = next(p for p in self.peluqueros if p.nombre == nombre_peluquero)
                
                if peluquero_terminado.cliente_actual:
                    self.nro_cliente_actual = peluquero_terminado.cliente_actual.id_cliente
                    
                self.procesar_fin_atencion(peluquero_terminado)

            elif self.evento_actual == 'Abandono':
                for cola in self.colas.values():
                    if cola and abs((cola[0].hora_llegada_cola + self.tolerancia_espera) - self.reloj_dia) < 0.001:
                        cliente_abandona = cola.pop(0)
                        self.nro_cliente_actual = cliente_abandona.id_cliente
                        break 

            elif self.evento_actual == 'Cierre Recepcion':
                if sum(len(c) for c in self.colas.values()) >= 3:
                    self.dias_con_cola_larga += 1
                self.cierres_totales += 1
                self.proxima_llegada = float('inf')
                self.proximo_cierre = float('inf')

            elif self.evento_actual == 'Cierre Peluquería':
                self.evaluar_guardado_fila()
                self.dia_actual += 1
                self.iteracion_actual += 1
                self.inicializar_dia()
                self.evento_actual = "Inicio de Día"
                self.evaluar_guardado_fila()
                self.iteracion_actual += 1
                self.limpiar_variables_de_fila()
                continue

            self.evaluar_guardado_fila()
            self.iteracion_actual += 1
            self.limpiar_variables_de_fila()

        porcentaje_libre_aprendiz = round((self.acumulador_tiempo_libre_aprendiz / self.reloj_absoluto) * 100, 2) if self.reloj_absoluto > 0 else 0.0
        probabilidad_cola = round(self.dias_con_cola_larga / self.cierres_totales, 2) if self.cierres_totales > 0 else 0.0

        # === PROCESAMIENTO DE COLUMNAS SIMULTÁNEAS ===
        max_clientes_simultaneos = max((len(fila[-1]) for fila in self.filas_a_mostrar), default=0)

        # Ya NO sumamos encabezados extra, mandamos la lista estática tal cual
        columnas_finales = list(COLUMNAS)

        filas_planas = []
        for fila in self.filas_a_mostrar:
            base = fila[:-1]
            datos_clientes = fila[-1]
            padding = ["-"] * (max_clientes_simultaneos - len(datos_clientes))
            filas_planas.append(base + datos_clientes + padding)

        metricas = {
            "pct_libre_aprendiz": porcentaje_libre_aprendiz,
            "max_sillas": self.maximo_sillas_usadas,
            "prob_cola_tres": probabilidad_cola,
            "max_clientes_mostrados": max_clientes_simultaneos
        }

        return filas_planas, columnas_finales, metricas

    def iniciar_atencion(self, peluquero, cliente):
        cliente.estado = f"Siendo Atendido por {peluquero.nombre}"
        rnd_atencion = random.random()
        
        if peluquero.nombre == "Aprendiz":
            tiempo_atencion = self.ap_a + rnd_atencion * (self.ap_b - self.ap_a)
        elif peluquero.nombre == "Veterano A":
            tiempo_atencion = self.va_a + rnd_atencion * (self.va_b - self.va_a)
        else:
            tiempo_atencion = self.vb_a + rnd_atencion * (self.vb_b - self.vb_a)
            
        peluquero.ocupar(cliente, self.reloj_dia + tiempo_atencion)

    def procesar_fin_atencion(self, peluquero):
        cola_activa = self.colas[peluquero.nombre]
        if cola_activa:
            siguiente_cliente = cola_activa.pop(0)
            self.iniciar_atencion(peluquero, siguiente_cliente)
        else:
            peluquero.liberar()

    def obtener_proximo_abandono(self):
        tiempos_abandono = [cola[0].hora_llegada_cola + self.tolerancia_espera for cola in self.colas.values() if cola]
        return min(tiempos_abandono) if tiempos_abandono else float('inf')

    def inicializar_dia(self):
        self.reloj_dia = 0.0
        for cola in self.colas.values(): cola.clear()
        for p in self.peluqueros: p.liberar()

        rnd_llegada = random.random()
        tiempo_llegada = self.llegada_a + rnd_llegada * (self.llegada_b - self.llegada_a)
        
        self.proxima_llegada = tiempo_llegada
        self.proximo_cierre = self.duracion_jornada
        self.rnd_llegada_actual = rnd_llegada
        self.tiempo_llegada_actual = tiempo_llegada
        self.nro_cliente_actual = "-"

    def evaluar_guardado_fila(self, forzar_guardado=False):
        if forzar_guardado or (self.reloj_absoluto >= self.minuto_inicio_mostrar and self.contador_filas_mostradas < self.cantidad_iteraciones_mostrar):
            self.registrar_fila_en_matriz()
            if not forzar_guardado and self.reloj_absoluto >= self.minuto_inicio_mostrar:
                self.contador_filas_mostradas += 1

    def limpiar_variables_de_fila(self):
        self.rnd_llegada_actual = None
        self.tiempo_llegada_actual = None
        self.rnd_preferencia_actual = None
        self.preferencia_actual = "-"
        self.nro_cliente_actual = "-"

    def registrar_fila_en_matriz(self):
        rnd_lleg_str = f"{self.rnd_llegada_actual:.2f}" if self.rnd_llegada_actual is not None else "-"
        t_lleg_str = f"{self.tiempo_llegada_actual:.2f}" if self.tiempo_llegada_actual is not None else "-"
        p_lleg_str = f"{self.proxima_llegada:.2f}" if self.proxima_llegada != float('inf') else "-"
        rnd_pref_str = f"{self.rnd_preferencia_actual:.2f}" if self.rnd_preferencia_actual is not None else "-"

        c_ap = len(self.colas["Aprendiz"])
        c_va = len(self.colas["Veterano A"])
        c_vb = len(self.colas["Veterano B"])

        cli_ap = self.aprendiz.cliente_actual.id_cliente if self.aprendiz.cliente_actual else "-"
        cli_va = self.veterano_a.cliente_actual.id_cliente if self.veterano_a.cliente_actual else "-"
        cli_vb = self.veterano_b.cliente_actual.id_cliente if self.veterano_b.cliente_actual else "-"

        pct_libre_ap = round((self.acumulador_tiempo_libre_aprendiz / self.reloj_absoluto) * 100, 2) if self.reloj_absoluto > 0 else 0.0
        prob_cola = round(self.dias_con_cola_larga / self.cierres_totales, 2) if self.cierres_totales > 0 else 0.00

        # === RECOLECTAR SOLO CLIENTES PRESENTES EN ESTE INSTANTE ===
        clientes_activos = []
        for p in self.peluqueros:
            if p.cliente_actual:
                clientes_activos.append(p.cliente_actual)
        for lista_cola in self.colas.values():
            for c_cola in lista_cola:
                clientes_activos.append(c_cola)
        
        clientes_activos.sort(key=lambda x: x.id_cliente)
        
        datos_clientes_fila = []
        for c in clientes_activos:
            sigla = MAPA_SIGLAS.get(c.estado, c.estado)
            datos_clientes_fila.append(f"C{c.id_cliente}: {sigla}")

        fila = [
            self.iteracion_actual, self.dia_actual,
            f"{self.reloj_dia:.2f}", f"{self.reloj_absoluto:.2f}",
            self.evento_actual, self.nro_cliente_actual,
            rnd_lleg_str, t_lleg_str, p_lleg_str, rnd_pref_str, self.preferencia_actual,
            self.aprendiz.estado, cli_ap, f"{self.aprendiz.fin_atencion:.2f}" if self.aprendiz.fin_atencion != float('inf') else "-", c_ap,
            self.veterano_a.estado, cli_va, f"{self.veterano_a.fin_atencion:.2f}" if self.veterano_a.fin_atencion != float('inf') else "-", c_va,
            self.veterano_b.estado, cli_vb, f"{self.veterano_b.fin_atencion:.2f}" if self.veterano_b.fin_atencion != float('inf') else "-", c_vb,
            f"{pct_libre_ap}%", self.maximo_sillas_usadas, f"{prob_cola}%",
            datos_clientes_fila
        ]
        self.filas_a_mostrar.append(fila)
        