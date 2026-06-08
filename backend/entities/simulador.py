import random
from entities.peluquero import Peluquero
from entities.cliente import Cliente

COLUMNAS = [
    "Fila", "Día", "Reloj Día", "Reloj Absoluto", "Evento", "Número de Cliente",
    "RND Llegada", "Tiempo Llegada", "Próxima Llegada",
    "RND Asignación", "Peluquero Asignado",
    "Estado Aprendiz", "Cliente Aprendiz", "Próx Fin Aprendiz", "Cola Aprendiz",
    "Estado Veterano A", "Cliente Vet A", "Próx Fin Vet A", "Cola Veterano A",
    "Estado Veterano B", "Cliente Vet B", "Próx Fin Vet B", "Cola Veterano B",
    "% Tiempo Libre Aprendiz", "Máximo de Sillas", "Prob cola mayor a 3 en cierre"
]

class Simulador:
    def __init__(self, X, i, j, params):
        self.X_tiempo = X
        self.i_iteraciones = i
        self.j_minuto = j

        # Parámetros del sistema
        self.lleg_a = params.get('lleg_a', 2.0)
        self.lleg_b = params.get('lleg_b', 12.0)
        self.ap_a = params.get('ap_a', 20.0)
        self.ap_b = params.get('ap_b', 30.0)
        self.va_a = params.get('va_a', 11.0)
        self.va_b = params.get('va_b', 13.0)
        self.vb_a = params.get('vb_a', 12.0)
        self.vb_b = params.get('vb_b', 18.0)
        
        self.prob_ap = params.get('prob_ap', 15.0) / 100.0
        self.prob_va = params.get('prob_va', 45.0) / 100.0

        self.duracion_dia = 480.0
        self.tiempo_tolerancia = 30.0

        # Entidades puras (sin parámetros estocásticos como atributos)
        self.aprendiz = Peluquero("Aprendiz")
        self.veterano_a = Peluquero("Veterano A")
        self.veterano_b = Peluquero("Veterano B")
        self.peluqueros = [self.aprendiz, self.veterano_a, self.veterano_b]

        self.reloj_dia = 0.0
        self.reloj_absoluto = 0.0
        self.dia_actual = 1
        self.iteracion_actual = 1
        self.id_cliente = 1

        self.cola = []
        
        self.total_abandonos = 0
        self.acum_tiempo_libre_ap = 0.0
        self.max_sillas = 0
        self.dias_cola_mayor_3 = 0
        self.cierres_procesados = 0

        self.prox_llegada = 0.0
        self.prox_cierre = self.duracion_dia
        self.evento_actual = "Inicio de Día"
        
        self.iteraciones_mostradas = 0  
        self.limpiar_randoms()
        self.filas = []

    def limpiar_randoms(self):
        self.rnd_lleg_str = "-"
        self.t_lleg_str = "-"
        self.rnd_pref_str = "-"
        self.pref_str = "-"
        # Se elimina el reinicio del flag visual "mostrado" ya que las entidades no lo manejan.

    def inicializar_dia(self):
        self.reloj_dia = 0.0
        self.cola.clear()
        for p in self.peluqueros:
            p.liberar()

        rnd = round(random.random(), 2)
        t_lleg = self.lleg_a + rnd * (self.lleg_b - self.lleg_a)
        
        self.prox_llegada = t_lleg
        self.prox_cierre = self.duracion_dia
        self.rnd_lleg_str = f"{rnd:.2f}"
        self.t_lleg_str = t_lleg 

    def obtener_prox_abandono(self):
        if not self.cola:
            return float('inf')
        return min(c.hora_llegada_cola + self.tiempo_tolerancia for c in self.cola)

    def intentar_registrar(self, es_ultima=False):
        if es_ultima or (self.reloj_absoluto >= self.j_minuto and self.iteraciones_mostradas < self.i_iteraciones):
            self.registrar_fila()
            if not es_ultima and self.reloj_absoluto >= self.j_minuto:
                self.iteraciones_mostradas += 1

    def ejecutar(self):
        self.inicializar_dia()
        self.evento_actual = "Inicio de Día"
        self.intentar_registrar()
        self.iteracion_actual += 1
        self.limpiar_randoms()

        while self.reloj_absoluto <= self.X_tiempo and self.iteracion_actual <= 100000:
            reloj_anterior_dia = self.reloj_dia
            prox_abandono = self.obtener_prox_abandono()

            eventos = {
                'Llegada Cliente': self.prox_llegada,
                'Fin Atencion Aprendiz': self.aprendiz.fin_atencion,
                'Fin Atencion Veterano A': self.veterano_a.fin_atencion,
                'Fin Atencion Veterano B': self.veterano_b.fin_atencion,
                'Abandono': prox_abandono,
                'Cierre Recepcion': self.prox_cierre
            }

            min_tiempo = min(eventos.values())

            # Detectar el próximo evento
            if min_tiempo == float('inf') or (self.reloj_dia >= self.duracion_dia and len(self.cola) == 0 and all(p.estado == 'Libre' for p in self.peluqueros)):
                proximo_evento = 'Cierre Peluquería'
                avance = 0
            else:
                proximo_evento = min(eventos, key=eventos.get)
                avance = min_tiempo - reloj_anterior_dia

            # SI EL PRÓXIMO EVENTO SUPERA EL TIEMPO X, SE CORTA LA SIMULACIÓN
            if self.reloj_absoluto + avance > self.X_tiempo:
                avance_restante = self.X_tiempo - self.reloj_absoluto
                self.reloj_absoluto += avance_restante
                if self.aprendiz.estado == "Libre":
                    self.acum_tiempo_libre_ap += avance_restante
                
                self.intentar_registrar(es_ultima=True)
                break

            self.evento_actual = proximo_evento
            
            if self.evento_actual != 'Cierre Peluquería':
                self.reloj_dia = min_tiempo
            
            self.reloj_absoluto += avance
            if self.aprendiz.estado == "Libre":
                self.acum_tiempo_libre_ap += avance

            if self.evento_actual == 'Llegada Cliente':
                if self.reloj_dia < self.duracion_dia:
                    rnd_lleg = round(random.random(), 2)
                    t_lleg = self.lleg_a + rnd_lleg * (self.lleg_b - self.lleg_a)
                    
                    self.prox_llegada = self.reloj_dia + t_lleg
                    self.rnd_lleg_str = f"{rnd_lleg:.2f}"
                    self.t_lleg_str = t_lleg
                else:
                    self.prox_llegada = float('inf')

                # 1. El Simulador tira el RND y decide la preferencia
                rnd_pref = round(random.random(), 2)
                if rnd_pref < self.prob_ap:
                    preferencia_asignada = "Aprendiz"
                elif rnd_pref < (self.prob_ap + self.prob_va):
                    preferencia_asignada = "Veterano A"
                else:
                    preferencia_asignada = "Veterano B"

                # 2. Creamos al cliente limpio
                nuevo_cliente = Cliente(self.id_cliente, preferencia_asignada)
                self.id_cliente += 1

                self.rnd_pref_str = f"{rnd_pref:.2f}"
                self.pref_str = nuevo_cliente.preferencia

                p_obj = self.aprendiz if nuevo_cliente.preferencia == "Aprendiz" else (self.veterano_a if nuevo_cliente.preferencia == "Veterano A" else self.veterano_b)

                # 3. Lógica de asignación de servidor o cola
                if p_obj.estado == "Libre":
                    nuevo_cliente.estado = f"Siendo Atendido por {p_obj.nombre}"
                    
                    # El Simulador calcula el tiempo de atención y se lo informa al peluquero
                    rnd_atencion = round(random.random(), 2)
                    if p_obj.nombre == "Aprendiz":
                        tiempo_at = self.ap_a + rnd_atencion * (self.ap_b - self.ap_a)
                    elif p_obj.nombre == "Veterano A":
                        tiempo_at = self.va_a + rnd_atencion * (self.va_b - self.va_a)
                    else:
                        tiempo_at = self.vb_a + rnd_atencion * (self.vb_b - self.vb_a)
                        
                    fin_at = self.reloj_dia + tiempo_at
                    p_obj.ocupar(nuevo_cliente, fin_at)
                else:
                    nuevo_cliente.estado = f"En Cola {p_obj.nombre}"
                    nuevo_cliente.hora_llegada_cola = self.reloj_dia
                    self.cola.append(nuevo_cliente)
                    self.max_sillas = max(self.max_sillas, len(self.cola))

            elif self.evento_actual == 'Fin Atencion Aprendiz':
                self.procesar_fin_atencion(self.aprendiz)
            elif self.evento_actual == 'Fin Atencion Veterano A':
                self.procesar_fin_atencion(self.veterano_a)
            elif self.evento_actual == 'Fin Atencion Veterano B':
                self.procesar_fin_atencion(self.veterano_b)

            elif self.evento_actual == 'Abandono':
                cliente_retirado = next((c for c in self.cola if abs((c.hora_llegada_cola + self.tiempo_tolerancia) - self.reloj_dia) < 0.001), None)
                if cliente_retirado:
                    self.cola.remove(cliente_retirado)
                    self.total_abandonos += 1

            elif self.evento_actual == 'Cierre Recepcion':
                if len(self.cola) >= 3:
                    self.dias_cola_mayor_3 += 1
                self.cierres_procesados += 1
                self.prox_llegada = float('inf')
                self.prox_cierre = float('inf')

            elif self.evento_actual == 'Cierre Peluquería':
                self.intentar_registrar(es_ultima=False)
                self.iteracion_actual += 1
                
                self.dia_actual += 1
                self.inicializar_dia()
                self.evento_actual = "Inicio de Día"
                self.intentar_registrar()
                self.iteracion_actual += 1
                
                self.limpiar_randoms()
                continue

            self.intentar_registrar(es_ultima=False)
            self.iteracion_actual += 1
            self.limpiar_randoms()

        pct_libre_ap = round((self.acum_tiempo_libre_ap / self.reloj_absoluto) * 100, 2) if self.reloj_absoluto > 0 else 0.0
        prob_cola = round(self.dias_cola_mayor_3 / self.cierres_procesados, 2) if self.cierres_procesados > 0 else 0.00

        metricas = {
            "pct_libre_aprendiz": pct_libre_ap,
            "max_sillas": self.max_sillas,
            "prob_cola_tres": prob_cola
        }

        return self.filas, COLUMNAS, metricas

    def procesar_fin_atencion(self, peluquero):
        siguiente = next((c for c in self.cola if c.preferencia == peluquero.nombre), None)
        if siguiente:
            self.cola.remove(siguiente)
            siguiente.estado = f"Siendo Atendido por {peluquero.nombre}"
            
            # El Simulador calcula el tiempo de atención y se lo informa al peluquero
            rnd_atencion = round(random.random(), 2)
            if peluquero.nombre == "Aprendiz":
                tiempo_at = self.ap_a + rnd_atencion * (self.ap_b - self.ap_a)
            elif peluquero.nombre == "Veterano A":
                tiempo_at = self.va_a + rnd_atencion * (self.va_b - self.va_a)
            else:
                tiempo_at = self.vb_a + rnd_atencion * (self.vb_b - self.vb_a)
                
            fin_at = self.reloj_dia + tiempo_at
            peluquero.ocupar(siguiente, fin_at)
        else:
            peluquero.liberar()

    def registrar_fila(self):
        p_lleg = round(self.prox_llegada, 2) if self.prox_llegada != float('inf') else "-"
        
        c_ap = sum(1 for c in self.cola if c.preferencia == "Aprendiz")
        c_va = sum(1 for c in self.cola if c.preferencia == "Veterano A")
        c_vb = sum(1 for c in self.cola if c.preferencia == "Veterano B")

        cli_ap = self.aprendiz.cliente_actual.id_cliente if self.aprendiz.cliente_actual else "-"
        cli_va = self.veterano_a.cliente_actual.id_cliente if self.veterano_a.cliente_actual else "-"
        cli_vb = self.veterano_b.cliente_actual.id_cliente if self.veterano_b.cliente_actual else "-"

        pct_libre_ap = round((self.acum_tiempo_libre_ap / self.reloj_absoluto) * 100, 2) if self.reloj_absoluto > 0 else 0.0
        prob_cola = round(self.dias_cola_mayor_3 / self.cierres_procesados, 2) if self.cierres_procesados > 0 else 0.00

        nro_cli = self.id_cliente - 1 if self.evento_actual == 'Llegada Cliente' else "-"

        fila = [
            self.iteracion_actual,
            self.dia_actual,
            round(self.reloj_dia, 2),
            round(self.reloj_absoluto, 2),
            self.evento_actual,
            nro_cli,
            self.rnd_lleg_str, self.t_lleg_str, p_lleg,
            self.rnd_pref_str, self.pref_str,
            self.aprendiz.estado, cli_ap, round(self.aprendiz.fin_atencion, 2) if self.aprendiz.fin_atencion != float('inf') else "-", c_ap,
            self.veterano_a.estado, cli_va, round(self.veterano_a.fin_atencion, 2) if self.veterano_a.fin_atencion != float('inf') else "-", c_va,
            self.veterano_b.estado, cli_vb, round(self.veterano_b.fin_atencion, 2) if self.veterano_b.fin_atencion != float('inf') else "-", c_vb,
            pct_libre_ap,            
            self.max_sillas,         
            prob_cola                
        ]
        self.filas.append(fila)