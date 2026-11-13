# Solucionador de Laberintos con Grafos (BFS vs DFS vs Dijkstra)

Proyecto universitario para la materia de Matemáticas Discretas / Algoritmos y Programación.
Implementa la conversión de una matriz de laberinto a un **Grafo no dirigido** representado mediante **Listas de Adyacencia** y compara el comportamiento de tres algoritmos fundamentales de búsqueda:
- **BFS (Búsqueda en Anchura)** — Cola FIFO
- **DFS (Búsqueda en Profundidad)** — Pila LIFO
- **DIJKSTRA (Camino de Costo Mínimo)** — Montículo de Mínimos (Min-Heap)

Incluye una interfaz gráfica interactiva en **Tkinter** con estética ciberpunk oscura, efectos de brillo de neón, animación de propagación en árbol y una **Arena de Competencia Simultánea** donde los 3 algoritmos compiten en tiempo real.

---

## 📁 Estructura del Proyecto

```text
proyecto_discretas/
├── laberintos/               # Carpeta con laberintos de prueba (.txt)
│   ├── ejemplo1.txt         # Laberinto simple 7x7
│   ├── ejemplo2.txt         # Laberinto 9x9 con atajos
│   ├── ejemplo3.txt         # Laberinto 7x7 que demuestra la diferencia de pasos BFS vs DFS
│   └── sin_solucion.txt     # Laberinto con meta bloqueada (prueba de robustez)
├── imagenes_laberintos/      # Imágenes PNG de prueba para la lectura por foto
│   ├── laberinto_7x7.png
│   ├── laberinto_9x9.png
│   └── laberinto_15x15.png
├── laberinto.py             # Carga, generación aleatoria y conversión Matriz -> Grafo
├── algoritmos.py            # Lógica pura de BFS y DFS (sin interfaz)
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
   - Es un grafo **no dirigido y sin pesos**, ya que caminar en cualquier sentido cuesta exactamente 1 paso.

3. **Estructura de Datos (Lista de Adyacencia):**
   - Se utiliza un diccionario en Python (`dict`):
     - **Clave:** Coordenada de la celda `(fila, columna)`.
     - **Valor:** Lista de coordenadas de celdas vecinas libres `[(f1, c1), (f2, c2), ...]`.

---

## 🔍 Comparación Teórica de los Tres Algoritmos

| Característica | BFS (Anchura) | DFS (Profundidad) | DIJKSTRA (Costo Mínimo) |
| :--- | :--- | :--- | :--- |
| **Estructura usada** | **Cola FIFO** (`collections.deque`) | **Pila LIFO** (`list` con `pop()`) | **Min-Heap / Montículo de Mínimos** (`heapq`) |
| **Estrategia** | Explora por niveles concéntricos (ondas en abanico). | Avanza por una rama hasta topar con pared y retrocede (*backtracking*). | Extrae siempre el nodo con menor distancia acumulada. |
| **Camino más corto** | **Garantizado** en grafos sin pesos. | **No garantizado** (depende del orden de vecinos). | **Garantizado** (óptimo siempre, con o sin pesos no negativos). |
| **Complejidad Temporal** | $O(V + E)$ | $O(V + E)$ | $O((V + E) \log V)$ |
| **Color Neón** | Cian eléctrico (`#00E5FF`) | Magenta neón (`#FF2BD6`) | Violeta eléctrico (`#B388FF`) |

---

## 🚀 Cómo ejecutar el proyecto

No requiere instalar librerías externas para la funcionalidad básica (solo Python 3 estándar con Tkinter).

### 1. Ejecutar la Interfaz Gráfica
```bash
python main.py
```

### 2. Ejecutar las Pruebas en Consola (Comparativa Triangular)
```bash
python test_etapa1.py
```

---

## 🎨 Controles de la Interfaz

- **◈ EJECUTAR BFS:** Búsqueda en anchura con garantía de distancia mínima.
- **◇ EJECUTAR DFS:** Búsqueda en profundidad exploratoria.
- **⬡ EJECUTAR DIJKSTRA:** Búsqueda por montículo de mínimos con costo uniforme.
- **⚔ COMPETIR LOS 3 (TIEMPO REAL):** Abre la arena con tres lienzos sincronizados paso a paso para comparar visualmente quién llega antes a la meta y quién encuentra el camino más corto.
- **↺ REINICIAR VISTA:** Limpia las rutas y restaura la cuadrícula base.
- **📁 CARGAR ARCHIVO (.TXT):** Carga laberintos personalizados desde disco.
- **📷 CARGAR DESDE IMAGEN:** Abre una foto de laberinto (con soporte para paredes de líneas finas o bloques completos), calibrando la cuadrícula con *Grid Line Snapping*.
- **🎲 GENERAR ALEATORIO:** Genera un laberinto nuevo con atajos proporcionales y selector de escala (21x21, 29x29, 37x37, 45x45).
- **Slider de Velocidad:** Ajusta el retardo (ms) de cada paso de la señal.

---

## 📷 Carga desde Imagen (OpenCV + NumPy)

### Instalación de dependencias
```bash
pip install opencv-python numpy
```

### Proceso de reconocimiento:
1. **Escala de Grises:** Simplifica la imagen a un solo canal de intensidad de luz.
2. **Binarización de Otsu:** Calcula el umbral matemático óptimo para separar paredes oscuras de caminos claros.
3. **Recorte y Contornos:** Descarta márgenes de papel o fondos irrelevantes.
4. **Muestreo en Cuadrícula:** Divide la región en celdas de igual tamaño y toma una muestra del núcleo de cada celda para evitar artefactos en las líneas.
5. **Calibración Interactiva:** Permite ajustar el número de filas y columnas si la imagen tiene ruido o perspectiva, y marcar Inicio y Meta con clics.

---

## 📝 Formato de los archivos `.txt`

Cualquier archivo de texto con filas de igual longitud formadas por ceros y unos separados por espacios o comas. Se pueden incluir comentarios iniciando la línea con `#`:

```text
# 0 = camino libre, 1 = pared
1 1 1 1 1
1 0 0 0 1
1 0 1 0 1
1 0 0 0 1
1 1 1 1 1
```
