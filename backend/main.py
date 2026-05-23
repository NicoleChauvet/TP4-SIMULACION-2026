from entities.simulador import Simulador

if __name__ == "__main__":
    print("_" * 50)
    print(" ---- SIMULADOR DE COLAS - PELUQUERÍA CENTRO ----")
    print("_" * 50)
    
    N = int(input("Ingrese cantidad de DÍAS a simular (N): "))
    X = float(input("Ingrese tiempo máximo a simular en minutos totales (X): "))
    i = int(input("Ingrese cuántas iteraciones mostrar (i): "))
    j = float(input("Ingrese desde qué minuto mostrar (j): "))
    print("_" * 50)

    # Creamos el objeto simulador y lo arrancamos
    simulador = Simulador(N, X, i, j)
    simulador.ejecutar()