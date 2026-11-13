"""
laberinto.py
------------
Módulo encargado de:
1. Cargar el laberinto desde un archivo de texto.
2. Generar laberintos aleatorios usando DFS con Backtracking (Árbol Generador).
3. Validar que las coordenadas de inicio y meta sean válidas.
4. Convertir la matriz de ceros y unos en un grafo representado con listas de adyacencia.
"""

import random


def generar_laberinto_aleatorio(filas=29, columnas=29, caminos_alternativos=True):
    """
    Genera un laberinto aleatorio utilizando el algoritmo de DFS con Backtracking.
    
    Fundamento teórico para la materia:
    El laberinto se genera tallando un ÁRBOL GENERADOR (Spanning Tree) sobre una cuadrícula
    inicialmente llena de paredes (1).
    - Empieza en una celda (1, 1).
    - Salta de a 2 casillas en una dirección aleatoria y tumba la pared intermedia.
    - Cuando llega a un callejón sin salida, retrocede (backtracking) usando una pila.
    - Al final, opcionalmente derriba paredes aleatorias para crear bifurcaciones
      y ciclos, permitiendo comparar cómo BFS encuentra el atajo mientras DFS toma el desvío.
    """
    # Forzamos dimensiones impares para que haya paredes perimetrales y pasillos alineados
    if filas % 2 == 0:
        filas += 1
    if columnas % 2 == 0:
        columnas += 1

    # Todo inicia como pared (1)
    matriz = [[1 for _ in range(columnas)] for _ in range(filas)]

    inicio_f, inicio_c = 1, 1
    matriz[inicio_f][inicio_c] = 0

    pila = [(inicio_f, inicio_c)]
    visitados = {(inicio_f, inicio_c)}

    # Saltos de 2 celdas: Arriba, Abajo, Izquierda, Derecha
    direcciones = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while pila:
        actual_f, actual_c = pila[-1]

        # Buscamos vecinos libres de saltar a 2 pasos
        vecinos_disponibles = []
        for df, dc in direcciones:
            vf = actual_f + df
            vc = actual_c + dc
            if 0 < vf < filas - 1 and 0 < vc < columnas - 1:
                if (vf, vc) not in visitados:
                    vecinos_disponibles.append((vf, vc, df, dc))

        if vecinos_disponibles:
            # Elegimos una dirección al azar
            vf, vc, df, dc = random.choice(vecinos_disponibles)

            # Derribamos la pared intermedia
            pared_f = actual_f + (df // 2)
            pared_c = actual_c + (dc // 2)
            matriz[pared_f][pared_c] = 0

            # Habilitamos la nueva celda
            matriz[vf][vc] = 0
            visitados.add((vf, vc))
            pila.append((vf, vc))
        else:
            # Retrocedemos en la pila si no hay salida
            pila.pop()

    # Opcional: derribar algunas paredes internas para crear bifurcaciones y ciclos
    # Esto hace más interesante la comparación entre BFS y DFS
    if caminos_alternativos:
        paredes_internas = []
        for f in range(2, filas - 2):
            for c in range(2, columnas - 2):
                if matriz[f][c] == 1:
                    # Si tiene caminos libres opuestos (horizontal o verticalmente)
                    if (matriz[f - 1][c] == 0 and matriz[f + 1][c] == 0) or \
                       (matriz[f][c - 1] == 0 and matriz[f][c + 1] == 0):
                        paredes_internas.append((f, c))

        # Abrimos atajos proporcionales al tamaño del laberinto para crear bifurcaciones
        cantidad_atajos = min(len(paredes_internas), max(3, (filas * columnas) // 75))
        for pared in random.sample(paredes_internas, cantidad_atajos):
            matriz[pared[0]][pared[1]] = 0

    return matriz

def cargar_laberinto_desde_archivo(ruta_archivo):
    """
    Lee un archivo de texto plano con la matriz del laberinto.
    Ignora líneas vacías y comentarios que comiencen con '#'.
    Retorna una matriz (lista de listas de enteros) o lanza ValueError si el formato es inválido.
    """
    matriz = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea_limpia = linea.strip()
                # Saltamos líneas vacías o de comentario
                if not linea_limpia or linea_limpia.startswith('#'):
                    continue

                # Soportamos tanto números separados por espacios o comas,
                # como líneas continuas de dígitos sin espacios (ej: '10001000...')
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

        # Validamos que todas las filas tengan la misma cantidad de columnas (matriz rectangular)
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
    """
    Verifica que el inicio y la meta estén dentro de la matriz
    y que ninguno se encuentre sobre una pared (valor 1).
    Retorna: (es_valido: bool, mensaje_error: str)
    """
    filas = len(matriz)
    columnas = len(matriz[0])

    fi, ci = inicio
    fm, cm = meta

    # 1. Comprobar que estén dentro de los límites
    if not (0 <= fi < filas and 0 <= ci < columnas):
        return False, f"La coordenada de inicio {inicio} está fuera de los límites ({filas}x{columnas})."

    if not (0 <= fm < filas and 0 <= cm < columnas):
        return False, f"La coordenada de meta {meta} está fuera de los límites ({filas}x{columnas})."

    # 2. Comprobar que no sean paredes
    if matriz[fi][ci] == 1:
        return False, f"La coordenada de inicio {inicio} es una pared (valor 1). Debe ser camino libre (0)."

    if matriz[fm][cm] == 1:
        return False, f"La coordenada de meta {meta} es una pared (valor 1). Debe ser camino libre (0)."

    return True, ""


def matriz_a_grafo(matriz):
    """
    ============================================================================
    CONVERSIÓN DE MATRIZ A GRAFO (LISTA DE ADYACENCIA)
    ============================================================================
    ¿Cómo modelamos el laberinto como un grafo?
    1. VÉRTICES (Nodos):
       Cada celda libre (matriz[f][c] == 0) se convierte en un nodo del grafo.
       El identificador de cada nodo es una tupla con su coordenada: (fila, columna).
       Las celdas con pared (1) NO forman parte del grafo porque no son transitables.

    2. ARISTAS (Conexiones):
       Existe una arista no dirigida entre dos celdas si:
       - Son adyacentes ortogonalmente: Arriba, Abajo, Izquierda o Derecha.
       - Ambas son celdas libres (valor 0).
       - Se encuentran dentro de los límites de la matriz.

    3. ESTRUCTURA DE DATOS:
       Usamos un diccionario de Python como lista de adyacencia:
       - Clave: Tupla con la coordenada de la celda (fila, columna).
       - Valor: Lista de tuplas con las celdas vecinas a las que se puede caminar.

       Ejemplo:
       grafo = {
           (1, 1): [(1, 2), (2, 1)],
           (1, 2): [(1, 1), (1, 3)],
           ...
       }
    ============================================================================
    """
    grafo = {}
    total_filas = len(matriz)
    total_columnas = len(matriz[0])

    # Movimientos ortogonales permitidos: (delta_fila, delta_columna)
    # Arriba, Abajo, Izquierda, Derecha
    movimientos = [
        (-1, 0),  # Arriba
        (1, 0),   # Abajo
        (0, -1),  # Izquierda
        (0, 1)    # Derecha
    ]

    for f in range(total_filas):
        for c in range(total_columnas):
            # Solo las celdas con camino libre (0) son nodos del grafo
            if matriz[f][c] == 0:
                nodo_actual = (f, c)
                grafo[nodo_actual] = []

                # Buscamos cuáles de sus 4 vecinos son caminos libres válidos
                for df, dc in movimientos:
                    vecino_f = f + df
                    vecino_c = c + dc

                    # Verificamos que el vecino esté dentro del tablero
                    if 0 <= vecino_f < total_filas and 0 <= vecino_c < total_columnas:
                        # Si el vecino también es un camino libre (0), añadimos la conexión
                        if matriz[vecino_f][vecino_c] == 0:
                            grafo[nodo_actual].append((vecino_f, vecino_c))

    return grafo


def imprimir_laberinto(matriz, inicio=None, meta=None, camino=None):
    """
    Función auxiliar para visualizar el laberinto en la consola de manera amigable.
    - Paredes: '█'
    - Caminos libres: ' '
    - Inicio: 'S'
    - Meta: 'E'
    - Camino solución: '*'
    """
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
