import sys
import ctypes
import tkinter as tk
from interfaz import InterfazLaberinto


def configurar_alta_resolucion():
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def main():
    configurar_alta_resolucion()
    raiz = tk.Tk()
    app = InterfazLaberinto(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
