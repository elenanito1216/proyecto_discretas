"""
imagen_a_matriz.py
------------------
Módulo universal para digitalizar imágenes de laberintos (fotos o capturas).

Soporta los dos formatos universales de laberintos:
1. LABERINTOS DE LÍNEAS / PAREDES FINAS (como el de la imagen subida):
   - Los caminos son habitaciones cuadradas y las paredes son líneas negras delgadas
     que separan los pasillos.
   - Detecta la cuadrícula de pasillos y construye la matriz de bloques (2N + 1).
2. LABERINTOS DE BLOQUES COMPLETOS:
   - Las paredes y los caminos ocupan celdas cuadradas completas.

Auto-detección inteligente:
- Mide la densidad de tinta negra: si es menor al 28%, clasifica automáticamente
  como laberinto de paredes finas; si es mayor, como laberinto de bloques.
- Permite al usuario calibrar interactivamente las divisiones y el tipo.
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox


def estimar_cuadricula_lineas(recortada_bin):
    """
    Detecta la distancia entre paredes (pitch) en laberintos de líneas delgadas
    buscando picos de densidad oscura en las columnas y filas.
    """
    alto, ancho = recortada_bin.shape
    col_dark = np.sum(recortada_bin == 0, axis=0)
    umbral = np.percentile(col_dark, 70)

    picos = [
        i for i in range(1, ancho - 1)
        if col_dark[i] > col_dark[i - 1] and col_dark[i] >= col_dark[i + 1] and col_dark[i] > umbral
    ]
    diffs = np.diff(picos)
    diffs_validas = diffs[diffs >= 8]

    if len(diffs_validas) > 0:
        pitch = float(np.median(diffs_validas))
    else:
        pitch = 16.0

    n_x = max(5, int(round(ancho / pitch)))
    n_y = max(5, int(round(alto / pitch)))
    return n_x, n_y


def estimar_cuadricula_bloques(recortada_bin):
    """Estima cantidad de bloques para laberintos gruesos tradicionales."""
    alto, ancho = recortada_bin.shape
    invertida = 255 - recortada_bin

    def estimar_eje(vector_sumas, longitud_total):
        norm = vector_sumas - vector_sumas.mean()
        ac = np.correlate(norm, norm, mode='full')
        ac = ac[len(vector_sumas) - 1:]

        picos = []
        for i in range(10, len(ac) - 1):
            if ac[i] > ac[i - 1] and ac[i] > ac[i + 1] and ac[i] > 0:
                picos.append((ac[i], i))

        if picos:
            picos.sort(reverse=True)
            primer_lag = picos[0][1]
            paso_celda = max(10, primer_lag // 2)
            estimado = round(longitud_total / paso_celda)
            if estimado % 2 == 0:
                estimado += 1
            return max(5, min(estimado, 51))
        return 15

    col_sums = np.sum(invertida == 255, axis=0)
    row_sums = np.sum(invertida == 255, axis=1)

    columnas = estimar_eje(col_sums, ancho)
    filas = estimar_eje(row_sums, alto)
    return filas, columnas


def procesar_imagen_laberinto(ruta_imagen, tipo_manual=None, divisiones_manual=None):
    """
    Procesa la imagen, recorta márgenes y convierte a matriz de 0s y 1s.
    Retorna diccionario con la matriz lista para BFS/DFS y visualización.
    """
    img = cv2.imread(ruta_imagen)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {ruta_imagen}")

    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 1. Recortar exactamente el marco del laberinto (descartar márgenes blancos)
    ys, xs = np.where(binaria == 0)
    if len(ys) == 0:
        raise ValueError("La imagen parece estar en blanco o no contiene paredes oscuras.")

    y1, y2 = ys.min(), ys.max()
    x1, x2 = xs.min(), xs.max()

    recortada_bin = binaria[y1:y2 + 1, x1:x2 + 1]
    recortada_color = img[y1:y2 + 1, x1:x2 + 1]
    alto, ancho = recortada_bin.shape

    # 2. Determinar si es de Líneas Delgadas o Bloques Gruesos
    pct_pared = np.mean(recortada_bin == 0) * 100
    if tipo_manual:
        tipo = tipo_manual
    else:
        # En laberintos de líneas, las paredes ocupan menos del 28% de los píxeles
        tipo = "lineas" if pct_pared < 28 else "bloques"

    imagen_con_grid = recortada_color.copy()

    # -------------------------------------------------------------------------
    # CASO 1: LABERINTO DE PAREDES FINAS / LÍNEAS (ej. la imagen subida)
    # -------------------------------------------------------------------------
    if tipo == "lineas":
        if divisiones_manual and divisiones_manual > 3:
            n_x = n_y = int(divisiones_manual)
        else:
            n_x, n_y = estimar_cuadricula_lineas(recortada_bin)

        # CALIBRACIÓN DE LÍNEAS EXACTAS (Grid Line Snapping):
        # En lugar de dividir ciegamente ancho/n_x (lo que acumula error de redondeo
        # y desfasa la cuadrícula en la esquina inferior derecha), alineamos cada
        # línea de la cuadrícula con el pico real de píxeles negros en su vecindad.
        col_lines = []
        for k in range(n_x + 1):
            exp_x = int(round(k * (ancho - 1) / n_x))
            win = range(max(0, exp_x - 3), min(ancho, exp_x + 4))
            best_x = max(win, key=lambda c: np.sum(recortada_bin[:, c] == 0))
            col_lines.append(best_x)

        row_lines = []
        for k in range(n_y + 1):
            exp_y = int(round(k * (alto - 1) / n_y))
            win = range(max(0, exp_y - 3), min(alto, exp_y + 4))
            best_y = max(win, key=lambda r: np.sum(recortada_bin[r, :] == 0))
            row_lines.append(best_y)

        filas_mat = 2 * n_y + 1
        cols_mat = 2 * n_x + 1
        matriz = np.ones((filas_mat, cols_mat), dtype=int)

        # Los centros de cada cuarto son siempre camino libre (0)
        for r in range(n_y):
            for c in range(n_x):
                matriz[2 * r + 1, 2 * c + 1] = 0

        # Muestreo robusto de paredes verticales internas
        for r in range(n_y):
            ys_start = row_lines[r] + 3
            ys_end = row_lines[r + 1] - 3
            for c in range(n_x - 1):
                xw = col_lines[c + 1]
                muestra = recortada_bin[ys_start:ys_end, max(0, xw - 2):min(ancho, xw + 3)]
                col_densities = np.mean(muestra == 0, axis=0) if muestra.size > 0 else [0]
                matriz[2 * r + 1, 2 * c + 2] = 1 if np.max(col_densities) > 0.40 else 0

        # Muestreo robusto de paredes horizontales internas
        for r in range(n_y - 1):
            yw = row_lines[r + 1]
            for c in range(n_x):
                xs_start = col_lines[c] + 3
                xs_end = col_lines[c + 1] - 3
                muestra = recortada_bin[max(0, yw - 2):min(alto, yw + 3), xs_start:xs_end]
                row_densities = np.mean(muestra == 0, axis=1) if muestra.size > 0 else [0]
                matriz[2 * r + 2, 2 * c + 1] = 1 if np.max(row_densities) > 0.40 else 0

        # Dibujar cuadrícula perfectamente alineada sobre la foto original
        for y_line in row_lines:
            cv2.line(imagen_con_grid, (0, y_line), (ancho, y_line), (0, 229, 255), 1)
        for x_line in col_lines:
            cv2.line(imagen_con_grid, (x_line, 0), (x_line, alto), (0, 229, 255), 1)

        # Detección de aberturas de entrada y salida en el perímetro
        aberturas = []
        # Borde superior
        for c in range(n_x):
            muestra_borde = recortada_bin[0:max(3, row_lines[0] + 2), col_lines[c] + 3 : col_lines[c + 1] - 3]
            if muestra_borde.size > 0 and np.mean(muestra_borde == 255) > 0.60:
                matriz[0, 2 * c + 1] = 0
                aberturas.append((0, 2 * c + 1))
        # Borde inferior
        for c in range(n_x):
            muestra_borde = recortada_bin[min(alto - 3, row_lines[-1] - 1):alto, col_lines[c] + 3 : col_lines[c + 1] - 3]
            if muestra_borde.size > 0 and np.mean(muestra_borde == 255) > 0.60:
                matriz[-1, 2 * c + 1] = 0
                aberturas.append((filas_mat - 1, 2 * c + 1))
        # Borde izquierdo
        for r in range(n_y):
            muestra_borde = recortada_bin[row_lines[r] + 3 : row_lines[r + 1] - 3, 0:max(3, col_lines[0] + 2)]
            if muestra_borde.size > 0 and np.mean(muestra_borde == 255) > 0.60:
                matriz[2 * r + 1, 0] = 0
                aberturas.append((2 * r + 1, 0))
        # Borde derecho
        for r in range(n_y):
            muestra_borde = recortada_bin[row_lines[r] + 3 : row_lines[r + 1] - 3, min(ancho - 3, col_lines[-1] - 1):ancho]
            if muestra_borde.size > 0 and np.mean(muestra_borde == 255) > 0.60:
                matriz[2 * r + 1, -1] = 0
                aberturas.append((2 * r + 1, cols_mat - 1))

        if len(aberturas) >= 2:
            inicio = aberturas[0]
            meta = aberturas[-1]
        elif len(aberturas) == 1:
            inicio = aberturas[0]
            meta = (filas_mat - 2, cols_mat - 2)
        else:
            inicio = (1, 1)
            meta = (filas_mat - 2, cols_mat - 2)

        return {
            "matriz": matriz.tolist(),
            "filas": filas_mat,
            "columnas": cols_mat,
            "inicio": inicio,
            "meta": meta,
            "tipo": "lineas",
            "cuartos": n_x,
            "imagen_con_grid": imagen_con_grid,
            "imagen_recortada": recortada_color
        }

    # -------------------------------------------------------------------------
    # CASO 2: LABERINTO DE BLOQUES COMPLETOS (ej. laberinto_7x7.png)
    # -------------------------------------------------------------------------
    else:
        if divisiones_manual and divisiones_manual > 2:
            filas = columnas = int(divisiones_manual)
        else:
            filas, columnas = estimar_cuadricula_bloques(recortada_bin)

        ancho_celda = ancho / columnas
        alto_celda = alto / filas

        matriz = []
        for f in range(filas):
            fila_actual = []
            y1_c = int(f * alto_celda)
            y2_c = int((f + 1) * alto_celda)
            yc1 = y1_c + int(alto_celda * 0.25)
            yc2 = y1_c + int(alto_celda * 0.75)

            for c in range(columnas):
                x1_c = int(c * ancho_celda)
                x2_c = int((c + 1) * ancho_celda)
                xc1 = x1_c + int(ancho_celda * 0.25)
                xc2 = x1_c + int(ancho_celda * 0.75)

                muestra = recortada_bin[yc1:yc2, xc1:xc2]
                es_camino = np.mean(muestra) > 128 if muestra.size > 0 else False
                fila_actual.append(0 if es_camino else 1)

                cv2.rectangle(imagen_con_grid, (x1_c, y1_c), (x2_c, y2_c), (0, 229, 255), 1)

            matriz.append(fila_actual)

        # Detectar inicio y meta
        libres = [(f, c) for f in range(filas) for c in range(columnas) if matriz[f][c] == 0]
        if len(libres) >= 2:
            inicio = libres[0]
            meta = libres[-1]
        else:
            inicio = (1, 1)
            meta = (filas - 2, columnas - 2)

        return {
            "matriz": matriz,
            "filas": filas,
            "columnas": columnas,
            "inicio": inicio,
            "meta": meta,
            "tipo": "bloques",
            "cuartos": columnas,
            "imagen_con_grid": imagen_con_grid,
            "imagen_recortada": recortada_color
        }


# ==============================================================================
# VENTANA DE CALIBRACIÓN Y PREVISUALIZACIÓN NEÓN
# ==============================================================================
class DialogoPrevisualizacionImagen:
    def __init__(self, padre, ruta_imagen, callback_exito):
        self.padre = padre
        self.ruta_imagen = ruta_imagen
        self.callback_exito = callback_exito

        self.ventana = tk.Toplevel(padre)
        self.ventana.title("CALIBRACIÓN // RECONOCIMIENTO VISUAL DE LABERINTO")
        self.ventana.geometry("1040x660")
        self.ventana.minsize(920, 580)
        self.ventana.configure(bg="#070B14")
        self.ventana.grab_set()

        self.tamano_canvas = 390
        self.foto_tk = None
        self.rectangulos_matriz = {}

        # Procesar imagen inicialmente con auto-detección
        self.resultado = procesar_imagen_laberinto(self.ruta_imagen)
        self.matriz = self.resultado["matriz"]
        self.filas = self.resultado["filas"]
        self.columnas = self.resultado["columnas"]
        self.inicio = self.resultado["inicio"]
        self.meta = self.resultado["meta"]
        self.tipo_actual = self.resultado["tipo"]

        self._crear_interfaz()
        self._actualizar_vistas()

    def _crear_interfaz(self):
        barra_sup = tk.Frame(self.ventana, bg="#0D1424", bd=1, highlightthickness=1, highlightbackground="#18243D")
        barra_sup.pack(fill=tk.X, padx=15, pady=(12, 8), ipady=5)

        tk.Label(
            barra_sup,
            text="TIPO DETECTADO:",
            font=("Consolas", 8, "bold"),
            bg="#0D1424",
            fg="#7A8C9E"
        ).pack(side=tk.LEFT, padx=(10, 4))

        self.var_tipo = tk.StringVar(value="lineas" if self.tipo_actual == "lineas" else "bloques")
        combo_tipo = tk.OptionMenu(
            barra_sup,
            self.var_tipo,
            "lineas",
            "bloques"
        )
        combo_tipo.config(
            bg="#05080F",
            fg="#00E5FF",
            activebackground="#18243D",
            activeforeground="#FFFFFF",
            font=("Consolas", 8, "bold"),
            highlightthickness=1,
            highlightbackground="#18243D",
            bd=0
        )
        combo_tipo["menu"].config(bg="#0D1424", fg="#00E5FF", font=("Consolas", 8))
        combo_tipo.pack(side=tk.LEFT, padx=4)

        tk.Label(
            barra_sup,
            text="CUARTOS / DIVISIONES:",
            font=("Consolas", 8, "bold"),
            bg="#0D1424",
            fg="#7A8C9E"
        ).pack(side=tk.LEFT, padx=(12, 4))

        self.entry_divs = tk.Entry(
            barra_sup,
            width=6,
            font=("Consolas", 10, "bold"),
            bg="#05080F",
            fg="#39FF14",
            insertbackground="#39FF14"
        )
        self.entry_divs.insert(0, str(self.resultado.get("cuartos", 40)))
        self.entry_divs.pack(side=tk.LEFT, padx=4)

        btn_recalc = tk.Button(
            barra_sup,
            text="🔄 RECALCULAR",
            font=("Consolas", 8, "bold"),
            bg="#18243D",
            fg="#00E5FF",
            activebackground="#00E5FF",
            activeforeground="#070B14",
            relief=tk.FLAT,
            command=self._recalcular_cuadricula
        )
        btn_recalc.pack(side=tk.LEFT, padx=10)

        lbl_ayuda = tk.Label(
            barra_sup,
            text="(Clic Izq: Inicio Verde | Clic Der: Meta Roja)",
            font=("Consolas", 8),
            bg="#0D1424",
            fg="#7A8C9E"
        )
        lbl_ayuda.pack(side=tk.RIGHT, padx=10)

        # Paneles lado a lado
        area = tk.Frame(self.ventana, bg="#070B14")
        area.pack(fill=tk.BOTH, expand=True, padx=15)

        # Panel 1: Foto con Grid
        p_izq = tk.LabelFrame(
            area,
            text=" 1. FOTO ORIGINAL + CUADRÍCULA CALIBRADA ",
            bg="#070B14",
            fg="#00E5FF",
            font=("Consolas", 9, "bold"),
            bd=1,
            highlightthickness=1,
            highlightbackground="#18243D"
        )
        p_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.canvas_foto = tk.Canvas(p_izq, width=self.tamano_canvas, height=self.tamano_canvas, bg="#05080F", highlightthickness=0)
        self.canvas_foto.pack(expand=True, pady=8)

        # Panel 2: Matriz Digitalizada
        p_der = tk.LabelFrame(
            area,
            text=" 2. MATRIZ DE GRAFO RECONSTRUIDA ",
            bg="#070B14",
            fg="#39FF14",
            font=("Consolas", 9, "bold"),
            bd=1,
            highlightthickness=1,
            highlightbackground="#18243D"
        )
        p_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.canvas_matriz = tk.Canvas(p_der, width=self.tamano_canvas, height=self.tamano_canvas, bg="#070B14", highlightthickness=0)
        self.canvas_matriz.pack(expand=True, pady=8)

        self.canvas_matriz.bind("<Button-1>", self._clic_izquierdo_inicio)
        self.canvas_matriz.bind("<Button-3>", self._clic_derecho_meta)

        # Barra inferior
        barra_inf = tk.Frame(self.ventana, bg="#070B14")
        barra_inf.pack(fill=tk.X, padx=15, pady=(8, 12))

        self.lbl_info = tk.Label(
            barra_inf,
            text="",
            font=("Consolas", 8, "bold"),
            bg="#070B14",
            fg="#00E5FF"
        )
        self.lbl_info.pack(side=tk.LEFT)

        btn_cancel = tk.Button(
            barra_inf,
            text="CANCELAR",
            font=("Consolas", 9, "bold"),
            bg="#18243D",
            fg="#7A8C9E",
            relief=tk.FLAT,
            command=self.ventana.destroy
        )
        btn_cancel.pack(side=tk.RIGHT, padx=(8, 0))

        btn_ok = tk.Button(
            barra_inf,
            text="✔ ACEPTAR Y RESOLVER EN EL SISTEMA",
            font=("Consolas", 9, "bold"),
            bg="#39FF14",
            fg="#070B14",
            activebackground="#FFFFFF",
            relief=tk.FLAT,
            command=self._confirmar
        )
        btn_ok.pack(side=tk.RIGHT)

    def _actualizar_vistas(self):
        img_grid = self.resultado["imagen_con_grid"]
        img_res = cv2.resize(img_grid, (self.tamano_canvas, self.tamano_canvas))
        _, buffer = cv2.imencode('.png', img_res)
        self.foto_tk = tk.PhotoImage(data=buffer.tobytes())

        self.canvas_foto.delete("all")
        self.canvas_foto.create_image(self.tamano_canvas // 2, self.tamano_canvas // 2, image=self.foto_tk)

        # Dibujar matriz digital
        self.canvas_matriz.delete("all")
        self.rectangulos_matriz.clear()

        tam_x = self.tamano_canvas / self.columnas
        tam_y = self.tamano_canvas / self.filas

        for f in range(self.filas):
            for c in range(self.columnas):
                x1 = c * tam_x
                y1 = f * tam_y
                x2 = x1 + tam_x
                y2 = y1 + tam_y

                coord = (f, c)
                if coord == self.inicio:
                    color = "#39FF14"
                    borde = "#FFFFFF"
                elif coord == self.meta:
                    color = "#FF2BD6"
                    borde = "#FFFFFF"
                elif self.matriz[f][c] == 1:
                    color = "#070B14"
                    borde = "#0C1322"
                else:
                    color = "#121A2C"
                    borde = "#1C2740"

                rect_id = self.canvas_matriz.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=borde,
                    width=1
                )
                self.rectangulos_matriz[coord] = rect_id

        tipo_txt = "Líneas Delgadas" if self.resultado["tipo"] == "lineas" else "Bloques Gruesos"
        self.lbl_info.config(
            text=f"TIPO: {tipo_txt} | MATRIZ: {self.filas}x{self.columnas} | INICIO: {self.inicio} | META: {self.meta}"
        )

    def _recalcular_cuadricula(self):
        try:
            tipo_sel = self.var_tipo.get()
            divs = int(self.entry_divs.get())

            self.resultado = procesar_imagen_laberinto(
                self.ruta_imagen,
                tipo_manual=tipo_sel,
                divisiones_manual=divs
            )
            self.matriz = self.resultado["matriz"]
            self.filas = self.resultado["filas"]
            self.columnas = self.resultado["columnas"]
            self.inicio = self.resultado["inicio"]
            self.meta = self.resultado["meta"]
            self.tipo_actual = self.resultado["tipo"]

            self._actualizar_vistas()

        except Exception as e:
            messagebox.showerror("Error al calibrar", str(e))

    def _clic_izquierdo_inicio(self, event):
        tam_x = self.tamano_canvas / self.columnas
        tam_y = self.tamano_canvas / self.filas
        c = int(event.x / tam_x)
        f = int(event.y / tam_y)

        if 0 <= f < self.filas and 0 <= c < self.columnas:
            if self.matriz[f][c] == 1:
                messagebox.showwarning("Pared", "No puedes seleccionar una pared como Inicio.")
                return
            self.inicio = (f, c)
            self._actualizar_vistas()

    def _clic_derecho_meta(self, event):
        tam_x = self.tamano_canvas / self.columnas
        tam_y = self.tamano_canvas / self.filas
        c = int(event.x / tam_x)
        f = int(event.y / tam_y)

        if 0 <= f < self.filas and 0 <= c < self.columnas:
            if self.matriz[f][c] == 1:
                messagebox.showwarning("Pared", "No puedes seleccionar una pared como Meta.")
                return
            self.meta = (f, c)
            self._actualizar_vistas()

    def _confirmar(self):
        self.callback_exito(self.matriz, self.inicio, self.meta)
        self.ventana.destroy()
