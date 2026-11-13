"""
test_etapa1.py
--------------
Script de prueba en consola para la Etapa 1.
Permite verificar:
1. La carga correcta del archivo .txt.
2. La conversión de la matriz a grafo con lista de adyacencia.
3. El funcionamiento de BFS y DFS, comparando pasos y nodos visitados.
4. El manejo de casos borde (laberinto sin solución, inicio en pared).
"""

from laberinto import cargar_laberinto_desde_archivo, matriz_a_grafo, validar_coordenadas, imprimir_laberinto
from algoritmos import bfs, dfs, dijkstra


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

    # Validamos coordenadas
    es_valido, error = validar_coordenadas(matriz, inicio, meta)
    if not es_valido:
        print(f"[VALIDACIÓN ESPERADA / RECHAZO]: {error}\n")
        return

    # Convertimos a grafo
    grafo = matriz_a_grafo(matriz)
    print(f"Grafo generado exitosamente con {len(grafo)} nodos transitables (caminos libres).")

    # Mostramos un ejemplo de nodo y sus adyacentes
    ejemplo_nodo = inicio if inicio in grafo else list(grafo.keys())[0]
    print(f"Ejemplo de adyacencia para el nodo {ejemplo_nodo}: {grafo.get(ejemplo_nodo, [])}")
    print("\nVisualización inicial del laberinto:")
    print(imprimir_laberinto(matriz, inicio=inicio, meta=meta))

    # Ejecutamos BFS
    resultado_bfs = bfs(grafo, inicio, meta)
    print("\n" + "-" * 30 + " RESULTADO BFS " + "-" * 30)
    print(f"¿Llegó a la meta?: {'SÍ' if resultado_bfs['exito'] else 'NO'}")
    print(f"Longitud del camino (pasos): {resultado_bfs['pasos']}")
    print(f"Total de celdas visitadas:   {resultado_bfs['total_visitados']}")
    if resultado_bfs['exito']:
        print("Camino encontrado (primeras y últimas coordenadas):")
        camino = resultado_bfs['camino']
        if len(camino) <= 6:
            print(f"  {camino}")
        else:
            print(f"  {camino[:3]} ... {camino[-3:]}")

    # Ejecutamos DFS
    resultado_dfs = dfs(grafo, inicio, meta)
    print("\n" + "-" * 30 + " RESULTADO DFS " + "-" * 30)
    print(f"¿Llegó a la meta?: {'SÍ' if resultado_dfs['exito'] else 'NO'}")
    print(f"Longitud del camino (pasos): {resultado_dfs['pasos']}")
    print(f"Total de celdas visitadas:   {resultado_dfs['total_visitados']}")
    if resultado_dfs['exito']:
        print("Camino encontrado (primeras y últimas coordenadas):")
        camino = resultado_dfs['camino']
        if len(camino) <= 6:
            print(f"  {camino}")
        else:
            print(f"  {camino[:3]} ... {camino[-3:]}")

    # Ejecutamos Dijkstra
    resultado_dijk = dijkstra(grafo, inicio, meta)
    print("\n" + "-" * 30 + " RESULTADO DIJKSTRA " + "-" * 30)
    print(f"¿Llegó a la meta?: {'SÍ' if resultado_dijk['exito'] else 'NO'}")
    print(f"Longitud del camino (pasos): {resultado_dijk['pasos']}")
    print(f"Total de celdas visitadas:   {resultado_dijk['total_visitados']}")
    if resultado_dijk['exito']:
        print("Camino encontrado (primeras y últimas coordenadas):")
        camino = resultado_dijk['camino']
        if len(camino) <= 6:
            print(f"  {camino}")
        else:
            print(f"  {camino[:3]} ... {camino[-3:]}")

    # Comparación
    print("\n" + "*" * 22 + " COMPARATIVA TRIANGULAR " + "*" * 22)
    if resultado_bfs['exito'] and resultado_dfs['exito'] and resultado_dijk['exito']:
        print(f"Pasos BFS:      {resultado_bfs['pasos']} (Óptimo)")
        print(f"Pasos DIJKSTRA: {resultado_dijk['pasos']} (Óptimo)")
        print(f"Pasos DFS:      {resultado_dfs['pasos']}")
        dif = resultado_dfs['pasos'] - resultado_bfs['pasos']
        if dif > 0:
            print(f"-> BFS y Dijkstra encontraron la ruta óptima, ahorrando {dif} pasos frente a DFS.")
        else:
            print("-> Los tres algoritmos encontraron rutas de igual longitud.")
        print(f"Celdas exploradas: BFS={resultado_bfs['total_visitados']} | DFS={resultado_dfs['total_visitados']} | DIJK={resultado_dijk['total_visitados']}")
    elif not resultado_bfs['exito'] and not resultado_dfs['exito']:
        print("Los tres algoritmos confirmaron que el laberinto NO tiene solución.")
    print("*" * 65 + "\n")


if __name__ == "__main__":
    # Prueba 1: Laberinto simple 7x7
    probar_archivo("ejemplo1.txt", inicio=(1, 1), meta=(5, 5))

    # Prueba 2: Laberinto 9x9 con atajo vs camino largo
    probar_archivo("ejemplo2.txt", inicio=(1, 1), meta=(7, 7))

    # Prueba 3: Laberinto 7x7 con bifurcación donde BFS y DFS difieren claramente en longitud
    probar_archivo("ejemplo3.txt", inicio=(1, 1), meta=(2, 3))

    # Prueba 4: Laberinto sin solución (meta amurallada)
    probar_archivo("sin_solucion.txt", inicio=(1, 1), meta=(3, 5))

    # Prueba 5: Caso de error intencional (inicio sobre pared)
    print(">>> Probando caso de error: Inicio colocado sobre una pared (0, 0)")
    probar_archivo("ejemplo1.txt", inicio=(0, 0), meta=(5, 5))
