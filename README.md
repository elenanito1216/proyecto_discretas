# Solucionador de Laberintos con Grafos (Algoritmo de Dijkstra)

Proyecto universitario para la materia de Matemáticas Discretas / Algoritmos y Programación.
Implementa la conversión de una matriz de laberinto a un **Grafo no dirigido** representado mediante **Listas de Adyacencia** y resuelve la ruta óptima mediante el **Algoritmo de Dijkstra** utilizando una **Cola de Prioridad (Min-Heap)**.

Incluye una interfaz gráfica interactiva en **Tkinter** con estética ciberpunk oscura, efectos de brillo de neón, animación de propagación en árbol y soporte para pantallas de alta resolución (High-DPI).

---

## 📁 Estructura del Proyecto

```text
proyecto_discretas/
├── laberintos/               # Carpeta con laberintos de prueba (.txt)
│   ├── ejemplo1.txt         # Laberinto simple 7x7
│   ├── ejemplo2.txt         # Laberinto 9x9 con atajos
│   ├── ejemplo3.txt         # Laberinto 7x7 con bifurcaciones
│   ├── sin_solucion.txt     # Laberinto con meta bloqueada (prueba de robustez)
│   └── laberinto_usuario.txt# Laberinto de cuadrícula 39x41
├── imagenes_laberintos/      # Imágenes PNG de prueba para la lectura por foto
│   ├── laberinto_7x7.png
│   ├── laberinto_9x9.png
│   └── laberinto_15x15.png
├── laberinto.py             # Carga, generación aleatoria y conversión Matriz -> Grafo
├── algoritmos.py            # Lógica pura del Algoritmo de Dijkstra (sin interfaz)
├── imagen_a_matriz.py       # Lectura de laberintos desde fotos usando OpenCV y NumPy
├── generar_imagenes_ejemplo.py # Generador de imágenes PNG de prueba
├── interfaz.py              # Interfaz gráfica y animación paso a paso con Tkinter
├── main.py                  # Archivo principal para ejecutar el programa
├── test_etapa1.py           # Script de pruebas por consola
└── README.md                # Este documento explicativo
```

---

## 🧠 ¿Cómo se relaciona el Laberinto con un Grafo?

Un laberinto representado en una cuadrícula o matriz se traduce a un **Grafo no dirigido** $G = (V, E)$ de la siguiente manera:

1. **Vértices o Nodos ($V$):**
   - Cada celda con valor `0` (camino libre) es un vértice del grafo.
   - Su identificador es la tupla de su coordenada: `(fila, columna)`.
   - Las celdas con valor `1` (pared) **no** forman parte del grafo, pues no son transitables.

2. **Aristas o Conexiones ($E$):**
   - Existe una arista entre dos celdas libres si son vecinas ortogonales directas (**Arriba, Abajo, Izquierda, Derecha**).
   - Es un grafo **no dirigido y con costo uniforme**, ya que caminar entre celdas vecinas cuesta 1 paso.

3. **Estructura de Datos (Lista de Adyacencia):**
   - Se utiliza un diccionario en Python (`dict`):
     - **Clave:** Coordenada de la celda `(fila, columna)`.
     - **Valor:** Lista de coordenadas de celdas vecinas libres `[(f1, c1), (f2, c2), ...]`.

---

## 🔍 Fundamento Teórico: Algoritmo de Dijkstra

| Propiedad | Descripción |
| :--- | :--- |
| **Estructura de Datos** | **Cola de Prioridad / Montículo de Mínimos (Min-Heap)** mediante `heapq`. |
| **Estrategia** | Expande progresivamente el nodo con menor distancia acumulada conocida desde el origen. |
| **Garantía Matemática** | **Camino más corto garantizado** (óptimo global). |
| **Complejidad Temporal** | $O((V + E) \log V)$ usando Min-Heap. |
| **Representación Visual** | Señal cian brillante (`#00E5FF`) propagándose en forma de árbol hacia la meta. |

---

## 🚀 Cómo ejecutar el proyecto

No requiere instalar librerías externas para la funcionalidad básica (solo Python 3 estándar con Tkinter).

### 1. Ejecutar la Interfaz Gráfica
```bash
python main.py
```

### 2. Ejecutar las Pruebas en Consola
```bash
python test_etapa1.py
```

---

## 🎨 Controles de la Interfaz

- **⬡ RESOLVER CON DIJKSTRA:** Ejecuta el algoritmo de Dijkstra con animación luminosa de propagación y trazado de la ruta óptima final.
- **↺ REINICIAR VISTA:** Limpia las rutas de exploración y restaura la cuadrícula base.
- **📁 CARGAR ARCHIVO (.TXT):** Carga laberintos personalizados desde disco (soporta números con espacios, comas o dígitos continuos).
- **📷 CARGAR DESDE IMAGEN:** Abre una foto de laberinto (con soporte para paredes de líneas finas o bloques completos), calibrando la cuadrícula con *Grid Line Snapping*.
- **🎲 GENERAR ALEATORIO:** Genera un laberinto nuevo con atajos proporcionales y selector de escala (21x21, 29x29, 37x37, 45x45).
- **Slider de Velocidad:** Ajusta el retardo (ms) de cada paso de la señal.

---

## 📷 Carga desde Imagen (OpenCV + NumPy)

### Instalación de dependencias opcionales
```bash
pip install opencv-python numpy
```

### Proceso de reconocimiento:
1. **Escala de Grises:** Simplifica la imagen a un solo canal de intensidad de luz.
2. **Binarización de Otsu:** Calcula el umbral matemático óptimo para separar paredes oscuras de caminos claros.
3. **Recorte y Contornos:** Descarta márgenes de papel o fondos irrelevantes.
4. **Muestreo en Cuadrícula (*Grid Line Snapping*):** Alinea los ejes de muestreo con los picos reales de píxeles oscuros para evitar deformaciones en las esquinas.
5. **Calibración Interactiva:** Permite ajustar el número de filas y columnas, y seleccionar Inicio y Meta con clics.

---

## 📝 Formato de los archivos `.txt`

Cualquier archivo de texto con filas de igual longitud formadas por ceros y unos (separados por espacios, comas o dígitos continuos). Se pueden incluir comentarios iniciando la línea con `#`:

```text
# 0 = camino libre, 1 = pared
10001
10101
10001
```
