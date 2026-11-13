"""
main.py
-------
Punto de entrada principal del proyecto de Algoritmos y Grafos.
Ejecuta la interfaz gráfica interactiva del solucionador de laberintos.
"""

import sys
import ctypes
import tkinter as tk
from interfaz import InterfazLaberinto


def configurar_alta_resolucion():
    """
    Activa el soporte nativo de Alta Resolución (DPI Awareness) en Windows.
    
    Por defecto, Windows escala las aplicaciones de Python/Tkinter mediante un
    filtrado bilineal borroso (en pantallas con escala al 125%, 150% o 4K).
    Al activar DPI Awareness, la interfaz se dibuja en resolución nativa
    100% nítida, sin desenfoque en textos, líneas ni efectos de neón.
    """
    if sys.platform == "win32":
        try:
            # Opción recomendada en Windows 8.1, 10 y 11:
            # 1 = PROCESS_SYSTEM_DPI_AWARE (resolución nítida según el monitor)
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                # Respaldo para Windows Vista / 7
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def main():
    # 1. Configuramos nitidez nativa de pantalla antes de crear la ventana
    configurar_alta_resolucion()

    # 2. Creamos la ventana principal de Tkinter
    raiz = tk.Tk()

    # 3. Inicializamos nuestra aplicación
    app = InterfazLaberinto(raiz)

    # 4. Iniciamos el bucle de eventos de la interfaz
    raiz.mainloop()


if __name__ == "__main__":
    main()
