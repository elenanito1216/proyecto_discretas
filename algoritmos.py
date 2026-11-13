"""
algoritmos.py
-------------
Módulo con las implementaciones de los tres algoritmos clásicos de búsqueda sobre grafos:
1. BFS (Breadth-First Search / Búsqueda en Anchura):
   - Utiliza una COLA (FIFO - primero en entrar, primero en salir).
   - Explora por "niveles" concéntricos alrededor del punto de partida.
   - GARANTIZA encontrar el camino más corto en grafos sin pesos.

2. DFS (Depth-First Search / Búsqueda en Profundidad):
   - Utiliza una PILA (LIFO - último en entrar, primero en salir).
   - Avanza por una rama hasta topar con pared y luego retrocede (backtracking).
   - NO garantiza el camino más corto, pero suele encontrar soluciones con patrones exploratorios.

3. DIJKSTRA (Camino de Costo Mínimo):
   - Utiliza una COLA DE PRIORIDAD (Min-Heap / Montículo de Mínimos con heapq).
   - En este laberinto, cada paso entre celdas vecinas tiene costo uniforme 1.
   - GARANTIZA encontrar el camino de menor costo (óptimo igual que BFS), expandiendo
     siempre el nodo con la menor distancia acumulada conocida.

Todos los algoritmos retornan:
- exito (bool): Si se llegó o no a la meta.
- camino (list): Lista de coordenadas (fila, col) desde el inicio hasta la meta.
- pasos (int): Cantidad de pasos del camino (aristas recorridas = longitud - 1).
- total_visitados (int): Cantidad total de celdas que el algoritmo tuvo que explorar.
- orden_visita (list): Orden exacto en que se fueron explorando las celdas (para la animación).
"""

from collections import deque
import heapq


def reconstruir_camino(padres, inicio, meta):
    """
    Función auxiliar para reconstruir el camino desde la meta hacia el inicio,
    siguiendo el diccionario de 'padres' que guardó cada algoritmo.
    Retorna la lista de coordenadas en orden desde inicio hasta meta.
    """
    camino = []
    nodo_actual = meta

    while nodo_actual is not None:
        camino.append(nodo_actual)
        nodo_actual = padres.get(nodo_actual)

    # El camino se construyó de meta a inicio, así que lo invertimos
    camino.reverse()

    # Si el camino empieza en inicio, la reconstrucción fue exitosa
    if camino and camino[0] == inicio:
        return camino
    return []


def bfs(grafo, inicio, meta):
    """
    Búsqueda en Anchura (BFS).
    Explora nivel por nivel usando una cola FIFO.
    """
    # Si el inicio o la meta no están en el grafo (por ejemplo, están en una pared o grafo vacío)
    if inicio not in grafo or meta not in grafo:
        return {
            "exito": False,
            "camino": [],
            "pasos": 0,
            "total_visitados": 0,
            "orden_visita": []
        }

    # Caso trivial: el inicio ya es la meta
    if inicio == meta:
        return {
            "exito": True,
            "camino": [inicio],
            "pasos": 0,
            "total_visitados": 1,
            "orden_visita": [inicio]
        }

    # Usamos deque de collections porque popleft() es O(1) a diferencia de una lista normal
    cola = deque([inicio])
    visitados = {inicio}
    orden_visita = [inicio]

    # Diccionario de padres: padres[hijo] = nodo_desde_el_que_llegamos
    # Nos servirá al final para rastrear el camino de regreso
    padres = {inicio: None}

    meta_encontrada = False

    while cola:
        actual = cola.popleft()

        # Si llegamos a la meta, detenemos la búsqueda
        if actual == meta:
            meta_encontrada = True
            break

        # Revisamos todos los vecinos conectados en el grafo
        for vecino in grafo.get(actual, []):
            if vecino not in visitados:
                visitados.add(vecino)
                orden_visita.append(vecino)
                padres[vecino] = actual
                cola.append(vecino)

    if meta_encontrada:
        camino = reconstruir_camino(padres, inicio, meta)
        pasos = len(camino) - 1
        return {
            "exito": True,
            "camino": camino,
            "pasos": pasos,
            "total_visitados": len(visitados),
            "orden_visita": orden_visita
        }
    else:
        # No se encontró camino (laberinto sin solución)
        return {
            "exito": False,
            "camino": [],
            "pasos": 0,
            "total_visitados": len(visitados),
            "orden_visita": orden_visita
        }


def dfs(grafo, inicio, meta):
    """
    Búsqueda en Profundidad (DFS).
    Explora profundamente cada rama usando una pila LIFO (implementada con una lista y pop()).
    """
    if inicio not in grafo or meta not in grafo:
        return {
            "exito": False,
            "camino": [],
            "pasos": 0,
            "total_visitados": 0,
            "orden_visita": []
        }

    if inicio == meta:
        return {
            "exito": True,
            "camino": [inicio],
            "pasos": 0,
            "total_visitados": 1,
            "orden_visita": [inicio]
        }

    # En DFS usamos una pila (LIFO). En Python, list.append() y list.pop() funcionan como pila.
    pila = [inicio]
    visitados = {inicio}
    orden_visita = [inicio]
    padres = {inicio: None}

    meta_encontrada = False

    while pila:
        actual = pila.pop()

        if actual == meta:
            meta_encontrada = True
            break

        # Para un comportamiento visual intuitivo en cuadrícula, invertimos los vecinos al meterlos a la pila,
        # así el primer vecino evaluado será el primero de la lista original.
        for vecino in reversed(grafo.get(actual, [])):
            if vecino not in visitados:
                visitados.add(vecino)
                orden_visita.append(vecino)
                padres[vecino] = actual
                pila.append(vecino)

    if meta_encontrada:
        camino = reconstruir_camino(padres, inicio, meta)
        pasos = len(camino) - 1
        return {
            "exito": True,
            "camino": camino,
            "pasos": pasos,
            "total_visitados": len(visitados),
            "orden_visita": orden_visita
        }
    else:
        return {
            "exito": False,
            "camino": [],
            "pasos": 0,
            "total_visitados": len(visitados),
            "orden_visita": orden_visita
        }


def dijkstra(grafo, inicio, meta):
    """
    Algoritmo de Dijkstra para caminos de costo mínimo.
    
    ¿Cómo funciona en este laberinto?
    - Cada movimiento entre celdas vecinas tiene costo = 1 (grafo no ponderado con costo uniforme).
    - Mantiene una cola de prioridad (min-heap) que extrae siempre el nodo con menor distancia acumulada.
    - Garantiza encontrar el camino más corto (óptimo), al igual que BFS.
    - La diferencia teórica clave: BFS usa una cola simple FIFO O(V + E), mientras que Dijkstra
      usa un montículo de mínimos O((V + E) log V).
    """
    if inicio not in grafo or meta not in grafo:
        return {
            "exito": False,
            "camino": [],
            "pasos": 0,
            "total_visitados": 0,
            "orden_visita": []
        }

    if inicio == meta:
        return {
            "exito": True,
            "camino": [inicio],
            "pasos": 0,
            "total_visitados": 1,
            "orden_visita": [inicio]
        }

    # distancias[nodo]: menor distancia conocida desde el inicio hasta 'nodo'
    distancias = {inicio: 0}
    padres = {inicio: None}

    # Cola de prioridad (min-heap): guarda tuplas (distancia, contador_insercion, nodo)
    # El contador entero sirve para desempatar sin comparar tuplas de coordenadas
    contador = 0
    cola_prioridad = [(0, contador, inicio)]

    visitados = set()
    orden_visita = []
    meta_encontrada = False

    while cola_prioridad:
        dist_actual, _, actual = heapq.heappop(cola_prioridad)

        # Si ya visitamos este nodo definitivamente, lo saltamos (poda estándar de Dijkstra)
        if actual in visitados:
            continue

        visitados.add(actual)
        orden_visita.append(actual)

        # Si alcanzamos la meta, detenemos la búsqueda
        if actual == meta:
            meta_encontrada = True
            break

        # Exploramos vecinos
        for vecino in grafo.get(actual, []):
            if vecino not in visitados:
                nueva_dist = dist_actual + 1  # Costo 1 por celda en la cuadrícula
                if nueva_dist < distancias.get(vecino, float('inf')):
                    distancias[vecino] = nueva_dist
                    padres[vecino] = actual
                    contador += 1
                    heapq.heappush(cola_prioridad, (nueva_dist, contador, vecino))

    if meta_encontrada:
        camino = reconstruir_camino(padres, inicio, meta)
        pasos = len(camino) - 1
        return {
            "exito": True,
            "camino": camino,
            "pasos": pasos,
            "total_visitados": len(visitados),
            "orden_visita": orden_visita
        }
    else:
        return {
            "exito": False,
            "camino": [],
            "pasos": 0,
            "total_visitados": len(visitados),
            "orden_visita": orden_visita
        }
