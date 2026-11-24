import heapq


def reconstruir_camino(padres, inicio, meta):
    camino = []
    nodo_actual = meta

    while nodo_actual is not None:
        camino.append(nodo_actual)
        nodo_actual = padres.get(nodo_actual)

    camino.reverse()

    if camino and camino[0] == inicio:
        return camino
    return []


def dijkstra(grafo, inicio, meta):
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

    distancias = {inicio: 0}
    padres = {inicio: None}
    contador = 0
    cola_prioridad = [(0, contador, inicio)]

    visitados = set()
    orden_visita = []
    meta_encontrada = False

    while cola_prioridad:
        dist_actual, _, actual = heapq.heappop(cola_prioridad)

        if actual in visitados:
            continue

        visitados.add(actual)
        orden_visita.append(actual)

        if actual == meta:
            meta_encontrada = True
            break

        for vecino in grafo.get(actual, []):
            if vecino not in visitados:
                nueva_dist = dist_actual + 1
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
