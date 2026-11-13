"""
generar_imagenes_ejemplo.py
---------------------------
Script para generar imágenes de laberintos limpias y nítidas
en formato PNG para probar la funcionalidad de entrada por imagen (Etapa 4).
"""

import cv2
import numpy as np
import os
from laberinto import cargar_laberinto_desde_archivo, generar_laberinto_aleatorio


def guardar_matriz_como_imagen(matriz, ruta_salida, tamano_celda=40, grosor_borde=2):
    """
    Convierte una matriz de 0s y 1s en una imagen PNG clara:
    - 1 (paredes): Negro
    - 0 (caminos): Blanco
    """
    filas = len(matriz)
    columnas = len(matriz[0])

    alto = filas * tamano_celda
    ancho = columnas * tamano_celda

    # Imagen blanca (255)
    imagen = np.ones((alto, ancho), dtype=np.uint8) * 255

    for f in range(filas):
        for c in range(columnas):
            if matriz[f][c] == 1:
                y1 = f * tamano_celda
                x1 = c * tamano_celda
                y2 = y1 + tamano_celda
                x2 = x1 + tamano_celda
                imagen[y1:y2, x1:x2] = 0  # Pared negra

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    cv2.imwrite(ruta_salida, imagen)
    print(f"Imagen generada con éxito: {ruta_salida} ({filas}x{columnas}, {ancho}x{alto}px)")


if __name__ == "__main__":
    carpeta_salida = "imagenes_laberintos"

    # Imagen 1: Basada en ejemplo1.txt (7x7)
    m1 = cargar_laberinto_desde_archivo("laberintos/ejemplo1.txt")
    guardar_matriz_como_imagen(m1, f"{carpeta_salida}/laberinto_7x7.png", tamano_celda=50)

    # Imagen 2: Basada en ejemplo2.txt (9x9)
    m2 = cargar_laberinto_desde_archivo("laberintos/ejemplo2.txt")
    guardar_matriz_como_imagen(m2, f"{carpeta_salida}/laberinto_9x9.png", tamano_celda=45)

    # Imagen 3: Laberinto aleatorio mediano (15x15)
    m3 = generar_laberinto_aleatorio(15, 15, caminos_alternativos=True)
    guardar_matriz_como_imagen(m3, f"{carpeta_salida}/laberinto_15x15.png", tamano_celda=30)
