import random


def generar_laberinto_aleatorio(filas=29, columnas=29, caminos_alternativos=True):
    if filas % 2 == 0:
        filas += 1
    if columnas % 2 == 0:
        columnas += 1

    matriz = [[1 for _ in range(columnas)] for _ in range(filas)]

    inicio_f, inicio_c = 1, 1
    matriz[inicio_f][inicio_c] = 0

    pila = [(inicio_f, inicio_c)]
    visitados = {(inicio_f, inicio_c)}
    direcciones = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while pila:
        actual_f, actual_c = pila[-1]
        vecinos_disponibles = []
        for df, dc in direcciones:
            vf = actual_f + df
            vc = actual_c + dc
            if 0 < vf < filas - 1 and 0 < vc < columnas - 1:
                if (vf, vc) not in visitados:
                    vecinos_disponibles.append((vf, vc, df, dc))

        if vecinos_disponibles:
            vf, vc, df, dc = random.choice(vecinos_disponibles)
            pared_f = actual_f + (df // 2)
            pared_c = actual_c + (dc // 2)
            matriz[pared_f][pared_c] = 0
            matriz[vf][vc] = 0
            visitados.add((vf, vc))
            pila.append((vf, vc))
        else:
            pila.pop()

    if caminos_alternativos:
        paredes_internas = []
        for f in range(2, filas - 2):
            for c in range(2, columnas - 2):
                if matriz[f][c] == 1:
                    if (matriz[f - 1][c] == 0 and matriz[f + 1][c] == 0) or \
                       (matriz[f][c - 1] == 0 and matriz[f][c + 1] == 0):
                        paredes_internas.append((f, c))

        cantidad_atajos = min(len(paredes_internas), max(3, (filas * columnas) // 75))
        for pared in random.sample(paredes_internas, cantidad_atajos):
            matriz[pared[0]][pared[1]] = 0

    return matriz


def cargar_laberinto_desde_archivo(ruta_archivo):
    matriz = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea_limpia = linea.strip()
                if not linea_limpia or linea_limpia.startswith('#'):
                    continue

                tokens = linea_limpia.replace(',', ' ').split()
                elementos = []
                for token in tokens:
                    if len(token) > 1 and all(c in ('0', '1') for c in token):
                        elementos.extend(list(token))
                    else:
                        elementos.append(token)

                fila = []
                for valor in elementos:
                    if valor not in ('0', '1'):
                        raise ValueError(
                            f"Valor inválido '{valor}' en línea {numero_linea}. "
                            "El laberinto solo debe contener 0 (camino) y 1 (pared)."
                        )
                    fila.append(int(valor))

                if fila:
                    matriz.append(fila)

        if not matriz:
            raise ValueError("El archivo está vacío o no contiene filas válidas.")

        longitud_primera_fila = len(matriz[0])
        for idx, fila in enumerate(matriz):
            if len(fila) != longitud_primera_fila:
                raise ValueError(
                    f"Fila {idx + 1} tiene {len(fila)} columnas, pero la primera fila tiene {longitud_primera_fila}. "
                    "El laberinto debe ser una cuadrícula rectangular regular."
                )

        return matriz

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")


def validar_coordenadas(matriz, inicio, meta):
    filas = len(matriz)
    columnas = len(matriz[0])

    fi, ci = inicio
    fm, cm = meta

    if not (0 <= fi < filas and 0 <= ci < columnas):
        return False, f"La coordenada de inicio {inicio} está fuera de los límites ({filas}x{columnas})."

    if not (0 <= fm < filas and 0 <= cm < columnas):
        return False, f"La coordenada de meta {meta} está fuera de los límites ({filas}x{columnas})."

    if matriz[fi][ci] == 1:
        return False, f"La coordenada de inicio {inicio} es una pared (valor 1). Debe ser camino libre (0)."

    if matriz[fm][cm] == 1:
        return False, f"La coordenada de meta {meta} es una pared (valor 1). Debe ser camino libre (0)."

    return True, ""


def matriz_a_grafo(matriz):
    grafo = {}
    total_filas = len(matriz)
    total_columnas = len(matriz[0])

    movimientos = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for f in range(total_filas):
        for c in range(total_columnas):
            if matriz[f][c] == 0:
                nodo_actual = (f, c)
                grafo[nodo_actual] = []

                for df, dc in movimientos:
                    vecino_f = f + df
                    vecino_c = c + dc

                    if 0 <= vecino_f < total_filas and 0 <= vecino_c < total_columnas:
                        if matriz[vecino_f][vecino_c] == 0:
                            grafo[nodo_actual].append((vecino_f, vecino_c))

    return grafo


def imprimir_laberinto(matriz, inicio=None, meta=None, camino=None):
    conjunto_camino = set(camino) if camino else set()

    lineas = []
    for f, fila in enumerate(matriz):
        caracteres_fila = []
        for c, valor in enumerate(fila):
            coord = (f, c)
            if coord == inicio:
                caracteres_fila.append(" S ")
            elif coord == meta:
                caracteres_fila.append(" E ")
            elif coord in conjunto_camino:
                caracteres_fila.append(" * ")
            elif valor == 1:
                caracteres_fila.append("███")
            else:
                caracteres_fila.append(" . ")
        lineas.append("".join(caracteres_fila))
    return "\n".join(lineas)
