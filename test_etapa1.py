from laberinto import cargar_laberinto_desde_archivo, matriz_a_grafo, validar_coordenadas, imprimir_laberinto
from algoritmos import dijkstra


def probar_archivo(nombre_archivo, inicio, meta):
    print("=" * 65)
    print(f"PROBANDO ARCHIVO: {nombre_archivo}")
    print(f"Inicio: {inicio} | Meta: {meta}")
    print("=" * 65)

    ruta = f"laberintos/{nombre_archivo}"
    try:
        matriz = cargar_laberinto_desde_archivo(ruta)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el archivo: {e}")
        return

    es_valido, error = validar_coordenadas(matriz, inicio, meta)
    if not es_valido:
        print(f"[VALIDACIÓN ESPERADA / RECHAZO]: {error}\n")
        return

    grafo = matriz_a_grafo(matriz)
    print(f"Grafo generado exitosamente con {len(grafo)} nodos transitables (caminos libres).")

    ejemplo_nodo = inicio if inicio in grafo else list(grafo.keys())[0]
    print(f"Ejemplo de adyacencia para el nodo {ejemplo_nodo}: {grafo.get(ejemplo_nodo, [])}")
    print("\nVisualización inicial del laberinto:")
    print(imprimir_laberinto(matriz, inicio=inicio, meta=meta))

    resultado = dijkstra(grafo, inicio, meta)
    print("\n" + "-" * 26 + " RESULTADO DIJKSTRA " + "-" * 26)
    print(f"¿Llegó a la meta?: {'SÍ' if resultado['exito'] else 'NO'}")
    print(f"Longitud del camino (pasos): {resultado['pasos']}")
    print(f"Total de celdas visitadas:   {resultado['total_visitados']}")
    if resultado['exito']:
        print("Camino óptimo encontrado (primeras y últimas coordenadas):")
        camino = resultado['camino']
        if len(camino) <= 6:
            print(f"  {camino}")
        else:
            print(f"  {camino[:3]} ... {camino[-3:]}")
    else:
        print("El algoritmo determinó que no existe ruta posible hasta la meta.")
    print("*" * 65 + "\n")


if __name__ == "__main__":
    probar_archivo("ejemplo1.txt", inicio=(1, 1), meta=(5, 5))
    probar_archivo("ejemplo2.txt", inicio=(1, 1), meta=(7, 7))
    probar_archivo("ejemplo3.txt", inicio=(1, 1), meta=(2, 3))
    probar_archivo("sin_solucion.txt", inicio=(1, 1), meta=(3, 5))
    print(">>> Probando caso de error: Inicio colocado sobre una pared (0, 0)")
    probar_archivo("ejemplo1.txt", inicio=(0, 0), meta=(5, 5))
