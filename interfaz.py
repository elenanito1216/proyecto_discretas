import ctypes
import math
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def configurar_alta_resolucion():
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

configurar_alta_resolucion()

from laberinto import (
    cargar_laberinto_desde_archivo,
    matriz_a_grafo,
    validar_coordenadas,
    generar_laberinto_aleatorio
)
from algoritmos import dijkstra
from imagen_a_matriz import DialogoPrevisualizacionImagen

TEMA = {
    "fondo_general": "#070B14",
    "panel": "#0D1424",
    "panel_borde": "#18243D",
    "terminal_fondo": "#05080F",
    "calle_fondo": "#121A2C",
    "calle_borde": "#1C2740",
    "pared_fondo": "#070B14",
    "pared_borde": "#0C1322",
    "neon_cian": "#00E5FF",
    "neon_magenta": "#FF2BD6",
    "neon_verde": "#39FF14",
    "neon_ambar": "#FFB300",
    "neon_azul": "#00B0FF",
    "texto_principal": "#E0E6ED",
    "texto_secundario": "#7A8C9E",
    "fuente_cyber": ("Segoe UI", 9, "bold"),
    "fuente_titulo": ("Consolas", 14, "bold"),
    "fuente_terminal": ("Consolas", 9),
    "fuente_terminal_bold": ("Consolas", 9, "bold")
}

def mezclar_colores(color1_hex, color2_hex, factor=0.5):
    c1 = color1_hex.lstrip('#')
    c2 = color2_hex.lstrip('#')

    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)

    factor = max(0.0, min(1.0, factor))

    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)

    return f"#{r:02x}{g:02x}{b:02x}".upper()

def deducir_padres_arbol(grafo, orden_visita, inicio):
    if not orden_visita:
        return {inicio: None}

    pos_visita = {nodo: idx for idx, nodo in enumerate(orden_visita)}
    padres = {inicio: None}

    for i in range(1, len(orden_visita)):
        nodo = orden_visita[i]
        vecinos_previos = [
            v for v in grafo.get(nodo, [])
            if v in pos_visita and pos_visita[v] < i
        ]
        if vecinos_previos:
            padres[nodo] = min(vecinos_previos, key=lambda v: pos_visita[v])

    return padres

class BotonNeon(tk.Frame):
    def __init__(self, parent, texto, color_neon, comando, font=None, icono="", **kwargs):
        super().__init__(parent, bg=color_neon, bd=1, relief=tk.FLAT, **kwargs)
        self.color_neon = color_neon
        self.comando = comando
        self.font = font or TEMA["fuente_cyber"]

        self.bg_reposo = TEMA["panel"]
        self.bg_hover = mezclar_colores(TEMA["panel"], color_neon, 0.22)
        self.fg_reposo = color_neon
        self.fg_hover = "#FFFFFF"

        texto_completo = f"{icono} {texto}" if icono else texto

        self.lbl = tk.Label(
            self,
            text=texto_completo,
            bg=self.bg_reposo,
            fg=self.fg_reposo,
            font=self.font,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.lbl.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.lbl.bind("<Enter>", self._on_enter)
        self.lbl.bind("<Leave>", self._on_leave)
        self.lbl.bind("<Button-1>", self._on_click)

    def _on_enter(self, _event):
        self.config(bg="#FFFFFF")
        self.lbl.config(bg=self.bg_hover, fg=self.fg_hover)

    def _on_leave(self, _event):
        self.config(bg=self.color_neon)
        self.lbl.config(bg=self.bg_reposo, fg=self.fg_reposo)

    def _on_click(self, _event):
        if self.comando:
            self.comando()

class InterfazLaberinto:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("MAZE SOLVER // Algoritmo de Dijkstra — Cyber Navigation Grid")
        self.ventana.geometry("1020x720")
        self.ventana.minsize(940, 660)
        self.ventana.configure(bg=TEMA["fondo_general"])

        self.matriz = []
        self.grafo = {}
        self.inicio = (1, 1)
        self.meta = (5, 5)

        self.animacion_id = None
        self.pulso_id = None
        self.esta_animando = False
        self.fase_pulso = 0.0

        self.ancho_canvas = 580
        self.alto_canvas = 580
        self.tamano_celda = 20
        self.margen_x = 0
        self.margen_y = 0

        self._crear_diseno()

        self.ventana.protocol("WM_DELETE_WINDOW", self._al_cerrar)

        self._cargar_laberinto_inicial()
        self._iniciar_bucle_pulso()

    def _al_cerrar(self):
        self.detener_animacion()
        if self.pulso_id is not None:
            try:
                self.ventana.after_cancel(self.pulso_id)
            except Exception:
                pass
        self.ventana.destroy()

    def _crear_diseno(self):
        encabezado = tk.Frame(
            self.ventana,
            bg=TEMA["panel"],
            bd=1,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=TEMA["panel_borde"]
        )
        encabezado.pack(fill=tk.X, padx=15, pady=(10, 8), ipady=5)

        lbl_logo = tk.Label(
            encabezado,
            text="⚡ MAZE SOLVER // ALGORITMO DE DIJKSTRA",
            font=TEMA["fuente_titulo"],
            bg=TEMA["panel"],
            fg=TEMA["neon_cian"]
        )
        lbl_logo.pack(side=tk.LEFT, padx=15)

        lbl_sub = tk.Label(
            encabezado,
            text="SISTEMA DE NAVEGACIÓN Y ANÁLISIS DE RUTAS EN GRAFOS",
            font=("Consolas", 9),
            bg=TEMA["panel"],
            fg=TEMA["texto_secundario"]
        )
        lbl_sub.pack(side=tk.RIGHT, padx=15)

        cuerpo = tk.Frame(self.ventana, bg=TEMA["fondo_general"])
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        panel_izq = tk.Frame(cuerpo, bg=TEMA["fondo_general"])
        panel_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        marco_canvas = tk.Frame(
            panel_izq,
            bg=TEMA["panel_borde"],
            bd=1,
            highlightthickness=1,
            highlightbackground=TEMA["neon_cian"]
        )
        marco_canvas.pack(anchor=tk.CENTER, expand=True)

        self.canvas = tk.Canvas(
            marco_canvas,
            width=self.ancho_canvas,
            height=self.alto_canvas,
            bg=TEMA["fondo_general"],
            highlightthickness=0
        )
        self.canvas.pack()

        self._crear_leyenda(panel_izq)

        panel_der = tk.Frame(
            cuerpo,
            bg=TEMA["panel"],
            bd=1,
            highlightthickness=1,
            highlightbackground=TEMA["panel_borde"]
        )
        panel_der.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0), ipadx=8, ipady=6)

        self._crear_seccion_titulo(panel_der, "MODO DE RESOLUCIÓN")

        BotonNeon(
            panel_der,
            texto="RESOLVER CON DIJKSTRA",
            color_neon=TEMA["neon_cian"],
            comando=self.ejecutar_dijkstra,
            icono="⬡"
        ).pack(fill=tk.X, padx=10, pady=(3, 5))

        BotonNeon(
            panel_der,
            texto="REINICIAR VISTA",
            color_neon=TEMA["neon_ambar"],
            comando=self.reiniciar_visualizacion,
            icono="↺"
        ).pack(fill=tk.X, padx=10, pady=(0, 8))

        self._crear_seccion_titulo(panel_der, "ORIGEN DE DATOS")

        BotonNeon(
            panel_der,
            texto="CARGAR ARCHIVO (.TXT)",
            color_neon=TEMA["neon_azul"],
            comando=self.cargar_archivo,
            icono="📁"
        ).pack(fill=tk.X, padx=10, pady=(3, 3))

        f_tam = tk.Frame(panel_der, bg=TEMA["panel"])
        f_tam.pack(fill=tk.X, padx=10, pady=(3, 2))

        tk.Label(
            f_tam,
            text="ESCALA:",
            font=("Consolas", 8, "bold"),
            bg=TEMA["panel"],
            fg=TEMA["texto_secundario"]
        ).pack(side=tk.LEFT)

        self.combo_tamano = tk.StringVar(value="29x29 (Grande)")
        menu_tam = tk.OptionMenu(
            f_tam,
            self.combo_tamano,
            "21x21 (Medio)",
            "29x29 (Grande - Recomendado)",
            "37x37 (Extremo)",
            "45x45 (Gigante)"
        )
        menu_tam.config(
            bg=TEMA["terminal_fondo"],
            fg=TEMA["neon_cian"],
            activebackground=TEMA["panel_borde"],
            activeforeground="#FFFFFF",
            font=("Consolas", 8, "bold"),
            highlightthickness=1,
            highlightbackground=TEMA["panel_borde"],
            bd=0,
            padx=4,
            pady=2
        )
        menu_tam["menu"].config(
            bg=TEMA["panel"],
            fg=TEMA["neon_cian"],
            activebackground=TEMA["neon_cian"],
            activeforeground=TEMA["fondo_general"],
            font=("Consolas", 8)
        )
        menu_tam.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

        BotonNeon(
            panel_der,
            texto="GENERAR ALEATORIO",
            color_neon=mezclar_colores(TEMA["neon_azul"], "#9C27B0", 0.35),
            comando=self.generar_aleatorio_seleccionado,
            icono="🎲"
        ).pack(fill=tk.X, padx=10, pady=(1, 4))

        BotonNeon(
            panel_der,
            texto="CARGAR DESDE IMAGEN",
            color_neon="#AB47BC",
            comando=self.cargar_desde_imagen,
            icono="📷"
        ).pack(fill=tk.X, padx=10, pady=(0, 8))

        self._crear_seccion_titulo(panel_der, "VELOCIDAD DE SEÑAL")

        marco_slider = tk.Frame(
            panel_der,
            bg=TEMA["terminal_fondo"],
            bd=1,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=TEMA["panel_borde"]
        )
        marco_slider.pack(fill=tk.X, padx=10, pady=(3, 8), ipady=3)

        self.slider_velocidad = tk.Scale(
            marco_slider,
            from_=1,
            to=120,
            orient=tk.HORIZONTAL,
            bg=TEMA["terminal_fondo"],
            fg=TEMA["neon_cian"],
            activebackground=TEMA["neon_cian"],
            troughcolor=TEMA["panel"],
            highlightthickness=0,
            font=("Consolas", 8),
            length=180
        )
        self.slider_velocidad.set(15)
        self.slider_velocidad.pack(fill=tk.X, padx=8)

        lbl_ms = tk.Label(
            marco_slider,
            text="DELAY PASO (ms) — Menor es más veloz",
            font=("Consolas", 7),
            bg=TEMA["terminal_fondo"],
            fg=TEMA["texto_secundario"]
        )
        lbl_ms.pack(pady=(0, 2))

        self._crear_seccion_titulo(panel_der, "SYS.LOG // RESULTADOS")

        terminal = tk.Frame(
            panel_der,
            bg=TEMA["terminal_fondo"],
            bd=1,
            highlightthickness=1,
            highlightbackground=TEMA["neon_cian"]
        )
        terminal.pack(fill=tk.BOTH, expand=True, padx=10, pady=(3, 5), ipady=3)

        self.lbl_term_algoritmo = self._linea_terminal(terminal, "> ALGORITMO:  ", "STANDBY")
        self.lbl_term_solucion  = self._linea_terminal(terminal, "> ESTADO:     ", "EN ESPERA")
        self.lbl_term_pasos     = self._linea_terminal(terminal, "> RUTA FINAL: ", "-- PASOS")
        self.lbl_term_visitados = self._linea_terminal(terminal, "> EXPLORADAS: ", "-- CELDAS")

        self.lbl_estado = tk.Label(
            panel_der,
            text="SISTEMA LISTO. SELECCIONE UN ALGORITMO.",
            font=("Consolas", 8),
            bg=TEMA["panel"],
            fg=TEMA["texto_secundario"]
        )
        self.lbl_estado.pack(side=tk.BOTTOM, pady=4)

    def _crear_seccion_titulo(self, padre, texto):
        marco = tk.Frame(padre, bg=TEMA["panel"])
        marco.pack(fill=tk.X, padx=10, pady=(5, 1))
        lbl = tk.Label(
            marco,
            text=f"// {texto}",
            font=("Consolas", 8, "bold"),
            bg=TEMA["panel"],
            fg=TEMA["texto_secundario"]
        )
        lbl.pack(side=tk.LEFT)

    def _linea_terminal(self, padre, etiqueta, valor_inicial):
        fila = tk.Frame(padre, bg=TEMA["terminal_fondo"])
        fila.pack(fill=tk.X, padx=8, pady=2)

        lbl_etiq = tk.Label(
            fila,
            text=etiqueta,
            font=TEMA["fuente_terminal"],
            bg=TEMA["terminal_fondo"],
            fg=TEMA["texto_secundario"]
        )
        lbl_etiq.pack(side=tk.LEFT)

        lbl_val = tk.Label(
            fila,
            text=valor_inicial,
            font=TEMA["fuente_terminal_bold"],
            bg=TEMA["terminal_fondo"],
            fg=TEMA["neon_verde"]
        )
        lbl_val.pack(side=tk.LEFT)
        return lbl_val

    def _crear_leyenda(self, padre):
        barra = tk.Frame(padre, bg=TEMA["fondo_general"])
        barra.pack(fill=tk.X, pady=(6, 2))

        def _badge(texto, color, fill_color):
            c = tk.Frame(barra, bg=TEMA["panel"], bd=1, highlightthickness=1, highlightbackground=color)
            c.pack(side=tk.LEFT, padx=5)
            punto = tk.Canvas(c, width=10, height=10, bg=fill_color, highlightthickness=0)
            punto.pack(side=tk.LEFT, padx=(5, 4), pady=2)
            tk.Label(c, text=texto, font=("Consolas", 8, "bold"), bg=TEMA["panel"], fg=color).pack(side=tk.LEFT, padx=(0, 5), pady=2)

        _badge("INICIO", TEMA["neon_verde"], TEMA["neon_verde"])
        _badge("META", TEMA["neon_magenta"], TEMA["neon_magenta"])
        _badge("DIJKSTRA", TEMA["neon_cian"], TEMA["neon_cian"])
        _badge("RUTA", TEMA["neon_ambar"], TEMA["neon_ambar"])
        _badge("CALLE", TEMA["texto_secundario"], TEMA["calle_fondo"])

    def centro_celda(self, f, c):
        cx = self.margen_x + (c * self.tamano_celda) + (self.tamano_celda / 2)
        cy = self.margen_y + (f * self.tamano_celda) + (self.tamano_celda / 2)
        return cx, cy

    def dibujar_laberinto(self):
        self.canvas.delete("all")

        if not self.matriz:
            return

        filas = len(self.matriz)
        columnas = len(self.matriz[0])

        self.tamano_celda = min(self.ancho_canvas // columnas, self.alto_canvas // filas)
        self.margen_x = (self.ancho_canvas - (columnas * self.tamano_celda)) // 2
        self.margen_y = (self.alto_canvas - (filas * self.tamano_celda)) // 2

        for f in range(filas):
            for c in range(columnas):
                x1 = self.margen_x + (c * self.tamano_celda)
                y1 = self.margen_y + (f * self.tamano_celda)
                x2 = x1 + self.tamano_celda
                y2 = y1 + self.tamano_celda

                if self.matriz[f][c] == 1:
                    color_fondo = TEMA["pared_fondo"]
                    color_borde = TEMA["pared_borde"]
                else:
                    color_fondo = TEMA["calle_fondo"]
                    color_borde = TEMA["calle_borde"]

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color_fondo,
                    outline=color_borde,
                    width=1,
                    tags="base_grid"
                )

        self._dibujar_halos_inicio_meta()

    def _dibujar_halos_inicio_meta(self):
        self.canvas.delete("halos_fijos")

        osc = 0.5 + 0.5 * math.sin(self.fase_pulso)

        for coord, color, tag_nodo in [(self.inicio, TEMA["neon_verde"], "inicio"), (self.meta, TEMA["neon_magenta"], "meta")]:
            cx, cy = self.centro_celda(coord[0], coord[1])
            r_base = max(4, self.tamano_celda * 0.42)

            r_ext = r_base * (1.15 + 0.25 * osc)
            c_halo1 = mezclar_colores(TEMA["fondo_general"], color, 0.18 + 0.15 * osc)
            self.canvas.create_oval(
                cx - r_ext, cy - r_ext, cx + r_ext, cy + r_ext,
                fill=c_halo1, outline="", tags="halos_fijos"
            )

            r_mid = r_base * 0.8
            c_halo2 = mezclar_colores(TEMA["fondo_general"], color, 0.55)
            self.canvas.create_oval(
                cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid,
                fill=c_halo2, outline="", tags="halos_fijos"
            )

            r_core = r_base * 0.45
            self.canvas.create_oval(
                cx - r_core, cy - r_core, cx + r_core, cy + r_core,
                fill=color, outline="#FFFFFF", width=1.5, tags="halos_fijos"
            )

    def _iniciar_bucle_pulso(self):
        try:
            if not self.ventana.winfo_exists():
                return
        except Exception:
            return
        self.fase_pulso = (self.fase_pulso + 0.14) % (2 * math.pi)
        if not self.esta_animando:
            self._dibujar_halos_inicio_meta()
        self.pulso_id = self.ventana.after(70, self._iniciar_bucle_pulso)

    def trazar_linea_glow(self, canvas, x1, y1, x2, y2, color_neon, grosor_base, tag="animacion"):
        c1 = mezclar_colores(TEMA["fondo_general"], color_neon, 0.22)
        canvas.create_line(
            x1, y1, x2, y2,
            width=max(4, int(grosor_base * 2.4)),
            fill=c1,
            capstyle=tk.ROUND,
            tags=tag
        )

        c2 = mezclar_colores(TEMA["fondo_general"], color_neon, 0.75)
        canvas.create_line(
            x1, y1, x2, y2,
            width=max(2, int(grosor_base * 1.3)),
            fill=c2,
            capstyle=tk.ROUND,
            tags=tag
        )

        canvas.create_line(
            x1, y1, x2, y2,
            width=max(1, int(grosor_base * 0.5)),
            fill="#FFFFFF",
            capstyle=tk.ROUND,
            tags=tag
        )

    def dibujar_nodo_glow(self, canvas, x, y, color_neon, r_base, tag="animacion"):
        c_halo = mezclar_colores(TEMA["fondo_general"], color_neon, 0.40)
        canvas.create_oval(
            x - r_base * 1.5, y - r_base * 1.5,
            x + r_base * 1.5, y + r_base * 1.5,
            fill=c_halo, outline="", tags=tag
        )
        canvas.create_oval(
            x - r_base * 0.7, y - r_base * 0.7,
            x + r_base * 0.7, y + r_base * 0.7,
            fill=color_neon, outline="#FFFFFF", width=1, tags=tag
        )

    def _cargar_laberinto_inicial(self):
        try:
            self.matriz = cargar_laberinto_desde_archivo("laberintos/ejemplo1.txt")
            self.inicio = (1, 1)
            self.meta = (len(self.matriz) - 2, len(self.matriz[0]) - 2)
            self.grafo = matriz_a_grafo(self.matriz)
            self.dibujar_laberinto()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar laberinto inicial: {e}")

    def reiniciar_visualizacion(self):
        self.detener_animacion()
        self.canvas.delete("animacion")
        self.canvas.delete("camino_final")
        self.dibujar_laberinto()
        self.lbl_term_algoritmo.config(text="STANDBY", fg=TEMA["texto_secundario"])
        self.lbl_term_solucion.config(text="EN ESPERA", fg=TEMA["texto_secundario"])
        self.lbl_term_pasos.config(text="-- PASOS", fg=TEMA["texto_secundario"])
        self.lbl_term_visitados.config(text="-- CELDAS", fg=TEMA["texto_secundario"])
        self.lbl_estado.config(text="VISTA REINICIADA // SISTEMA EN ESPERA.")

    def detener_animacion(self):
        if self.animacion_id is not None:
            self.ventana.after_cancel(self.animacion_id)
            self.animacion_id = None
        self.esta_animando = False

    def cargar_archivo(self):
        self.detener_animacion()
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de laberinto",
            initialdir="laberintos",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        try:
            nueva_matriz = cargar_laberinto_desde_archivo(ruta)
            filas = len(nueva_matriz)
            columnas = len(nueva_matriz[0])

            nuevo_inicio = (1, 1) if nueva_matriz[1][1] == 0 else None
            nueva_meta = (filas - 2, columnas - 2) if nueva_matriz[filas - 2][columnas - 2] == 0 else None

            if nuevo_inicio is None or nueva_meta is None:
                libres = [(f, c) for f in range(filas) for c in range(columnas) if nueva_matriz[f][c] == 0]
                if len(libres) < 2:
                    messagebox.showerror("Error", "El laberinto requiere al menos dos celdas libres.")
                    return
                nuevo_inicio, nueva_meta = libres[0], libres[-1]

            valido, msg = validar_coordenadas(nueva_matriz, nuevo_inicio, nueva_meta)
            if not valido:
                messagebox.showerror("Coordenadas inválidas", msg)
                return

            self.matriz = nueva_matriz
            self.inicio = nuevo_inicio
            self.meta = nueva_meta
            self.grafo = matriz_a_grafo(self.matriz)

            self.reiniciar_visualizacion()
            nombre = ruta.replace("\\", "/").split("/")[-1]
            self.lbl_estado.config(text=f"CARGADO: {nombre} ({filas}x{columnas})")

        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def generar_aleatorio_seleccionado(self):
        texto_opcion = self.combo_tamano.get()
        dim = 29
        for parte in texto_opcion.split():
            if "x" in parte:
                try:
                    dim = int(parte.split("x")[0])
                    break
                except ValueError:
                    pass
        self.generar_aleatorio(filas=dim, columnas=dim)

    def generar_aleatorio(self, filas=29, columnas=29):
        self.detener_animacion()
        self.matriz = generar_laberinto_aleatorio(filas=filas, columnas=columnas, caminos_alternativos=True)
        self.inicio = (1, 1)
        self.meta = (len(self.matriz) - 2, len(self.matriz[0]) - 2)
        self.grafo = matriz_a_grafo(self.matriz)
        self.reiniciar_visualizacion()
        self.lbl_estado.config(text=f"LABERINTO ALEATORIO GENERADO ({len(self.matriz)}x{len(self.matriz[0])}).")

    def cargar_desde_imagen(self):
        self.detener_animacion()
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto de laberinto",
            initialdir="imagenes_laberintos",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        try:
            DialogoPrevisualizacionImagen(self.ventana, ruta, self._aplicar_laberinto_desde_imagen)
        except Exception as e:
            messagebox.showerror("Error al procesar imagen", str(e))

    def _aplicar_laberinto_desde_imagen(self, matriz, inicio, meta):
        self.matriz = matriz
        self.inicio = inicio
        self.meta = meta
        self.grafo = matriz_a_grafo(self.matriz)
        self.reiniciar_visualizacion()
        filas = len(matriz)
        columnas = len(matriz[0])
        self.lbl_estado.config(text=f"LABERINTO CARGADO DESDE IMAGEN ({filas}x{columnas}).")

    def ejecutar_algoritmo(self, tipo_algoritmo="DIJKSTRA"):
        return self.ejecutar_dijkstra()

    def ejecutar_dijkstra(self):
        if self.esta_animando:
            self.detener_animacion()

        self.canvas.delete("animacion")
        self.canvas.delete("camino_final")

        if not self.grafo:
            self.grafo = matriz_a_grafo(self.matriz)

        resultado = dijkstra(self.grafo, self.inicio, self.meta)
        color_exploracion = TEMA["neon_cian"]

        padres = deducir_padres_arbol(self.grafo, resultado["orden_visita"], self.inicio)

        self.lbl_term_algoritmo.config(text="DIJKSTRA", fg=color_exploracion)
        self.lbl_term_solucion.config(
            text="PROPAGANDO..." if resultado["exito"] else "ANALIZANDO...",
            fg=TEMA["neon_cian"]
        )
        self.lbl_term_pasos.config(text="-- PASOS", fg=TEMA["texto_secundario"])
        self.lbl_term_visitados.config(text="0 CELDAS", fg=TEMA["neon_verde"])

        self.esta_animando = True
        self.lbl_estado.config(text="PROPAGANDO SEÑAL // DIJKSTRA (MIN-HEAP)...")

        self._animar_arbol_exploracion(
            0,
            resultado["orden_visita"],
            padres,
            resultado["camino"],
            resultado["exito"],
            resultado["pasos"],
            color_exploracion
        )

    def _animar_arbol_exploracion(self, indice, orden_visita, padres, camino_final, exito, pasos_totales, color_neon):
        if not self.esta_animando:
            return

        if indice < len(orden_visita):
            nodo_actual = orden_visita[indice]
            nodo_padre = padres.get(nodo_actual)

            if nodo_padre is not None:
                x1, y1 = self.centro_celda(nodo_padre[0], nodo_padre[1])
                x2, y2 = self.centro_celda(nodo_actual[0], nodo_actual[1])

                grosor = max(2, self.tamano_celda * 0.16)
                self.trazar_linea_glow(self.canvas, x1, y1, x2, y2, color_neon, grosor, tag="animacion")

                r_dot = max(2, self.tamano_celda * 0.12)
                self.dibujar_nodo_glow(self.canvas, x2, y2, color_neon, r_dot, tag="animacion")

            self.lbl_term_visitados.config(text=f"{indice + 1} CELDAS", fg=color_neon)

            velocidad = self.slider_velocidad.get()
            self.animacion_id = self.ventana.after(
                velocidad,
                self._animar_arbol_exploracion,
                indice + 1,
                orden_visita,
                padres,
                camino_final,
                exito,
                pasos_totales,
                color_neon
            )
        else:
            if exito and camino_final:
                self.lbl_term_solucion.config(text="RUTA CONFIRMADA", fg=TEMA["neon_verde"])
                self.lbl_estado.config(text="TRAZANDO RUTA ÓPTIMA FINAL...")
                self._animar_camino_progresivo(0, camino_final, pasos_totales)
            else:
                self.esta_animando = False
                self.lbl_term_solucion.config(text="SIN RUTA POSIBLE", fg="#FF1744")
                self.lbl_estado.config(text="EXPLORACIÓN FINALIZADA // NO HAY RUTA A LA META.")
                messagebox.showwarning(
                    "Sin Solución",
                    "El algoritmo agotó las calles transitables sin encontrar conexión con la meta."
                )

    def _animar_camino_progresivo(self, indice, camino, pasos_totales):
        if not self.esta_animando:
            return

        if indice < len(camino) - 1:
            n1 = camino[indice]
            n2 = camino[indice + 1]

            x1, y1 = self.centro_celda(n1[0], n1[1])
            x2, y2 = self.centro_celda(n2[0], n2[1])

            grosor = max(3, self.tamano_celda * 0.28)
            self.trazar_linea_glow(self.canvas, x1, y1, x2, y2, TEMA["neon_ambar"], grosor, tag="camino_final")

            self.lbl_term_pasos.config(text=f"{indice + 1} / {pasos_totales} PASOS", fg=TEMA["neon_ambar"])

            vel = max(10, int(self.slider_velocidad.get() * 0.8))
            self.animacion_id = self.ventana.after(
                vel,
                self._animar_camino_progresivo,
                indice + 1,
                camino,
                pasos_totales
            )
        else:
            self.lbl_term_pasos.config(text=f"{pasos_totales} PASOS", fg=TEMA["neon_ambar"])
            self.lbl_estado.config(text="¡OBJETIVO ALCANZADO // ANÁLISIS COMPLETADO!")
            self._destello_final(0)

    def _destello_final(self, fase):
        if fase == 0:
            self.canvas.itemconfig("camino_final", fill="#FFFFFF")
            self.animacion_id = self.ventana.after(110, self._destello_final, 1)
        elif fase == 1:
            self.canvas.itemconfig("camino_final", fill="#FFE082")
            self.animacion_id = self.ventana.after(110, self._destello_final, 2)
        else:
            self.canvas.itemconfig("camino_final", fill=TEMA["neon_ambar"])
            self.esta_animando = False
            self._dibujar_halos_inicio_meta()
