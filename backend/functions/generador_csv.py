import csv
import os

def inicializar_csv(nombre_archivo="resultado_simulacion.csv"):
    # Asegurar que si la carpeta resultados no existe, se cree (opcional, o guardarlo en la raíz)
    # Definimos las columnas estrictas que pide el Trabajo Práctico
    columnas = [
        "Iteracion", "Dia", "Reloj_Absoluto", "Reloj_Dia", "Evento", 
        "RND_Llegada", "T_Llegada", "Prox_Llegada",
        "RND_Preferencia", "Preferencia_Cliente",
        "Aprendiz_Estado", "Aprendiz_Fin", 
        "VetA_Estado", "VetA_Fin", 
        "VetB_Estado", "VetB_Fin", 
        "Tamaño_Cola", "Total_Abandonos"
    ]
    
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(columnas)
    return nombre_archivo

def agregar_fila_csv(nombre_archivo, datos_fila):
    with open(nombre_archivo, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(datos_fila)