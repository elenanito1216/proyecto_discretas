# Solucionador de Laberintos con Teoría de Grafos y Algoritmo de Dijkstra

Proyecto académico para la asignatura de **Matemáticas Discretas / Algoritmos y Programación**.  
El sistema implementa la abstracción de laberintos bidimensionales hacia **Grafos No Dirigidos** representados mediante **Listas de Adyacencia** y encuentra la ruta de longitud mínima utilizando el **Algoritmo de Dijkstra** implementado con una **Cola de Prioridad (Min-Heap)**.

Incluye una interfaz gráfica interactiva desarrollada en **Tkinter** con estética *Cyberpunk / Night Navigation Grid*, simulación de brillo neón multi-capa (Glow), animación de propagación en árbol de búsqueda, reconocimiento de imágenes mediante visión artificial y soporte nativo para monitores de alta densidad de píxeles (High-DPI).

---

## 📁 Estructura del Repositorio

```text
proyecto_discretas/
├── laberintos/                     # Archivos de prueba en formato plano (.txt)
│   ├── ejemplo1.txt               # Laberinto clásico 7x7
│   ├── ejemplo2.txt               # Laberinto 9x9 con rutas redundantes
│   ├── ejemplo3.txt               # Laberinto 7x7 con bifurcaciones
│   ├── sin_solucion.txt           # Caso de prueba con meta inalcanzable
│   └── laberinto_complejo.txt     # Laberinto denso de 39x41 celdas
├── imagenes_laberintos/            # Fotografías y capturas de laberintos
│   ├── laberinto_7x7.png
│   ├── laberinto_9x9.png
│   └── laberinto_15x15.png
├── algoritmos.py                  # Algoritmo de Dijkstra puro (sin interfaz ni dependencias GUI)
├── laberinto.py                   # Modelado de grafos, parsing de archivos y generador aleatorio
├── imagen_a_matriz.py             # Pipeline de visión artificial (OpenCV + NumPy)
├── interfaz.py                    # Interfaz gráfica interactiva, animaciones y telemetría
├── main.py                        # Punto de entrada principal de la aplicación
├── test_etapa1.py                 # Suite de pruebas automatizadas por consola
├── generar_imagenes_ejemplo.py    # Generador de imágenes sintéticas de prueba
└── README.md                      # Documentación técnica y fundamentos teóricos
```

---

## 🧠 Modelado Matemático: Del Laberinto al Grafo

### 1. Definición Formal del Grafo
Un laberinto en una matriz de dimensiones $M \times N$ se formaliza como un grafo no dirigido y ponderado de manera uniforme:

$$G = (V, E)$$

- **Conjunto de Vértices ($V$):**  
  Cada celda transitable (donde el valor de la matriz es `0`, correspondiente a un camino libre) se define como un vértice $v \in V$.  
  Cada vértice está unívocamente identificado por su tupla de coordenadas discretas:
  $$v = (f, c) \quad \text{donde } 0 \le f < M \text{ y } 0 \le c < N$$
  Las celdas con valor `1` representan muros o paredes impenetrables; **no** forman parte del conjunto $V$.

- **Conjunto de Aristas ($E$):**  
  Existe una arista no dirigida $\{u, v\} \in E$ si y solo si los vértices $u=(f_u, c_u)$ y $v=(f_v, c_v)$ son celdas libres adyacentes ortogonalmente:
  $$|f_u - f_v| + |c_u - c_v| = 1$$
  Las conexiones diagonales no están permitidas.

- **Función de Costo ($w$):**  
  En un laberinto de casillas uniformes, el costo de atravesar cualquier arista es unitario:
  $$w(u, v) = 1 \quad \forall \{u, v\} \in E$$

### 2. Estructura de Datos en Memoria: Lista de Adyacencia
En lugar de una matriz de adyacencia de tamaño $|V| \times |V|$ (que requeriría memoria $O(|V|^2)$ y sería dispersa ya que el grado máximo de cualquier nodo es 4), se emplea una **Lista de Adyacencia** representada mediante un diccionario de Python (`dict`):

- **Clave:** Tupla de coordenadas `(f, c)`.
- **Valor:** Lista de tuplas `[(f_1, c_1), (f_2, c_2), ...]` con los vecinos transitables inmediatos.

```python
grafo = {
    (1, 1): [(1, 2), (2, 1)],
    (1, 2): [(1, 1), (1, 3)],
    (2, 1): [(1, 1), (3, 1)]
}
```

---

## 🔍 Fundamento del Algoritmo de Dijkstra

### 1. Principio de Funcionamiento
El Algoritmo de Dijkstra resuelve el problema del camino más corto desde un único origen (*Single-Source Shortest Path*) hacia todos los demás nodos o hasta un nodo destino específico.

1. **Inicialización:**
   - Se mantiene una tabla de distancias mínimas conocidas desde el origen:
     $$\text{distancias}[v] = \begin{cases} 0 & \text{si } v = v_{\text{inicio}} \\ \infty & \text{en otro caso} \end{cases}$$
   - Se mantiene un registro de predecesores `padres[v]` para permitir la reconstrucción del camino óptimo.
   - Se utiliza una **Cola de Prioridad (Min-Heap)** implementada con la biblioteca estándar `heapq`.

2. **Relajación de Aristas:**
   En cada paso, se extrae el nodo $u$ con menor distancia acumulada $d(u)$. Para cada vecino transitable $v \in \text{vecinos}(u)$:
   $$\text{nueva\_distancia} = d(u) + 1$$
   Si $\text{nueva\_distancia} < \text{distancias}[v]$, se actualiza $\text{distancias}[v]$, se establece $\text{padres}[v] = u$, y se inserta $(d(v), v)$ en el montículo.

3. **Reconstrucción del Camino:**
   Una vez que se extrae el nodo destino $v_{\text{meta}}$, se reconstruye la trayectoria comenzando en $v_{\text{meta}}$ y siguiendo la cadena de predecesores en `padres` hasta alcanzar $v_{\text{inicio}}$, invirtiendo el orden al final.

### 2. Análisis de Complejidad
- **Complejidad Temporal:**  
  Utilizando una cola de prioridad basada en un montículo binario (Min-Heap):
  $$O((|V| + |E|) \log |V|)$$
  Dado que en una cuadrícula cada nodo tiene a lo sumo 4 vecinos ortogonales, $|E| \le 4|V|$, por lo que la complejidad temporal en laberintos es asintóticamente $O(|V| \log |V|)$.
- **Complejidad Espacial:**  
  $$O(|V|)$$  
  Requerida para almacenar la tabla de distancias, el diccionario de predecesores, el conjunto de nodos explorados y el montículo.

---

## 🎲 Generación Procedural de Laberintos (Árbol Generador y Atajos)

El módulo `laberinto.py` implementa generación procedural de laberintos mediante dos fases:

1. **Árbol de Expansión Mínima (Spanning Tree) mediante Backtracking:**
   - La cuadrícula se inicializa completamente bloqueada con paredes (`1`).
   - Las celdas de coordenadas impares `(2i + 1, 2j + 1)` representan las habitaciones transitables.
   - Desde una celda inicial, un recorrido en profundidad con pila (*DFS Backtracking*) avanza 2 unidades en una dirección aleatoria, derribando la pared intermedia.
   - Al finalizar, el laberinto resultante es un **árbol**: contiene un único camino simple entre cualquier par de celdas y no posee ciclos.

2. **Apertura de Rutas Alternativas (Ciclos y Bifurcaciones):**
   - Para que el laberinto ofrezca verdaderas decisiones de optimización para Dijkstra, se habilitan `caminos_alternativos=True`.
   - Se seleccionan aleatoriamente paredes internas que separan pasillos transitables y se abren, introduciendo **ciclos**. Esto permite que existan rutas más largas y atajos más cortos, donde Dijkstra demuestra su capacidad de encontrar el óptimo global.

---

## 🖥️ Interfaz Gráfica y Renderizado Neón (Tkinter)

### 1. Soporte Nativo de Alta Resolución (High-DPI Awareness)
En sistemas Windows con pantallas 2K, 4K o escalado al 125%/150%, las ventanas estándar de Tkinter sufren de escalado por mapa de bits borroso (*DPI virtualization*). En `main.py` e `interfaz.py` se activa la compatibilidad directa con el subsistema de ventanas mediante llamadas nativas de Windows API:
```python
ctypes.windll.shcore.SetProcessDpiAwareness(1)
```

### 2. Simulación Óptica de Brillo Neón (Glow Multi-Capa)
Tkinter no incluye soporte nativo para efectos de sombreado, desenfoque gaussiano o canal alfa (RGBA) en primitivas vectoriales del `Canvas`. Para lograr el resplandor neón sin librerías pesadas, se implementó el algoritmo de interpolación de color `mezclar_colores`:

$$\text{Canal}_{\text{final}} = \text{Canal}_1 + (\text{Canal}_2 - \text{Canal}_1) \times \text{factor}$$

Cada arista o nodo trazado se compone de tres capas concéntricas:
1. **Capa Externa (Resplandor difuso):** Trazo ancho (grosor $\times 2.4$) con color neón mezclado al 22% sobre el fondo oscuro.
2. **Capa Media (Cuerpo luminoso):** Trazo intermedio (grosor $\times 1.3$) con color neón puro al 75%.
3. **Capa Interna (Núcleo de energía):** Trazo fino blanco brillante (`#FFFFFF`) con terminación redondeada (`capstyle=ROUND`).

### 3. Animación de la Red de Búsqueda
La visualización reproduce el árbol de expansión generado por Dijkstra:
- La función `deducir_padres_arbol` mapea la jerarquía padre-hijo del orden de exploración en tiempo $O(|V|)$.
- Cada paso dibuja un pulso de luz desde el nodo padre hacia el nuevo nodo descubierto, actualizando en tiempo real el contador de telemetría de celdas visitadas.
- Al llegar a la meta, se traza la ruta ganadora en color ámbar neón con un destello final (*flare*) de confirmación.

---

## 📷 Visión Artificial: Lectura de Laberintos desde Fotos (`imagen_a_matriz.py`)

Para permitir que el usuario suba fotografías de laberintos impresos o capturas de pantalla, se construyó un pipeline de procesamiento digital de imágenes con OpenCV y NumPy:

```
[ Imagen Cruda ]
       │
       ▼
1. Conversión a Escala de Grises (cv2.cvtColor)
       │
       ▼
2. Binarización Adaptativa de Otsu (cv2.threshold con OTSU)
       │
       ▼
3. Detección de Bounding Box y Recorte de Bordes
       │
       ▼
4. Alineación por Densidad de Proyección (Grid Line Snapping)
       │
       ▼
5. Muestreo Dual de Paredes (Líneas finas vs Bloques)
       │
       ▼
6. Detección Automática de Accesos Perimetrales (Inicio y Meta)
       │
       ▼
[ Matriz Discreta de Ceros y Unos ]
```

### Detalle de las Etapas:
1. **Binarización de Otsu:** Determina automáticamente el umbral óptimo de intensidad minimizando la varianza intra-clase entre paredes y caminos.
2. **Grid Line Snapping:** Cuando una foto tiene una cuadrícula grande (como 39x41), pequeños errores de redondeo causan que las esquinas queden desfasadas. Se calculan las proyecciones horizontales y verticales (sumas de píxeles negros por línea) y se ajustan las coordenadas de muestreo a los picos reales de las líneas de la cuadrícula.
3. **Muestreo Dual:** Analiza tanto el centro de cada celda como los bordes medianos que conectan con celdas adyacentes para detectar tanto paredes gruesas de bloques como paredes delgadas de trazo simple.
4. **Detección Perimetral:** Examina el contorno exterior de la matriz para localizar aperturas naturales en el borde, asignándolas como punto de Inicio y Meta.

---

## 🚀 Guía de Instalación y Ejecución

### Requisitos Previos
- **Python 3.8 o superior** con soporte para Tkinter.
- Para la función de lectura de imágenes (opcional pero recomendada):
  ```bash
  pip install opencv-python numpy
  ```

### Instrucciones de Ejecución

1. **Iniciar la Aplicación con Interfaz Gráfica:**
   ```bash
   python main.py
   ```

2. **Ejecutar la Suite de Pruebas de Dijkstra por Consola:**
   ```bash
   python test_etapa1.py
   ```

3. **Generar Imágenes Sintéticas de Ejemplo:**
   ```bash
   python generar_imagenes_ejemplo.py
   ```

---

## 📝 Formato de Archivos de Laberinto (`.txt`)

Los archivos de texto deben representar una matriz bidimensional donde:
- `0`: Celda transitable (camino libre).
- `1`: Pared o celda no transitable.

El analizador (`cargar_laberinto_desde_archivo`) es flexible y admite:
- Dígitos continuos (`10001`).
- Dígitos separados por espacios (`1 0 0 0 1`) o comas (`1, 0, 0, 0, 1`).
- Líneas de comentarios que comiencen con `#`.
- Espacios en blanco y saltos de línea adicionales.

Ejemplo:
```text
# Laberinto 5x5 de prueba
1 1 1 1 1
1 0 0 0 1
1 1 1 0 1
1 0 0 0 1
1 1 1 1 1
```

---

## 🎓 Banco de Preguntas y Respuestas para Evaluación Académica

A continuación se presentan 5 preguntas teóricas y prácticas fundamentales para la sustentación o examen de este proyecto:

---

### Pregunta 1: Representación de Grafos
**¿Por qué es computacionalmente preferible utilizar una Lista de Adyacencia en lugar de una Matriz de Adyacencia para representar este tipo de laberinto?**

**Respuesta:**  
En un laberinto en cuadrícula de dimensiones $M \times N$, el número de vértices es $|V| \le M \times N$. Debido a la restricción del movimiento ortogonal, cada celda libre puede conectarse como máximo a 4 vecinos directos (arriba, abajo, izquierda, derecha). Por ende, el número total de aristas satisface $|E| \le 4|V|$.  
- Una **Matriz de Adyacencia** requeriría una matriz de tamaño $|V| \times |V|$, con un consumo espacial de $O(|V|^2)$, donde más del 99% de los elementos serían ceros (grafo disperso).
- Una **Lista de Adyacencia** solo almacena las aristas reales que existen, consumiendo un espacio de $O(|V| + |E|) = O(|V|)$ y permitiendo iterar sobre los vecinos transitables de cualquier celda en tiempo $O(1)$.

---

### Pregunta 2: Optimización del Algoritmo de Dijkstra
**¿Cuál es la función del Montículo de Mínimos (Min-Heap) en el algoritmo de Dijkstra y cómo impacta en la complejidad temporal?**

**Respuesta:**  
En cada iteración, el algoritmo de Dijkstra debe seleccionar de entre todos los nodos pendientes aquel que posea la menor distancia tentativa acumulada.  
- Si se utilizara una lista o arreglo desordenado, encontrar el nodo mínimo requeriría una búsqueda secuencial de $O(|V|)$, llevando la complejidad global del algoritmo a $O(|V|^2)$.
- Al emplear un **Min-Heap** (`heapq` en Python), la extracción del nodo con distancia mínima (`heappop`) se realiza en tiempo $O(\log |V|)$ y la inserción de nuevos caminos relajados (`heappush`) toma $O(\log |V|)$. Esto reduce la complejidad total a $O((|V| + |E|) \log |V|)$, lo que hace factible resolver laberintos de miles de celdas de forma instantánea.

---

### Pregunta 3: Garantía de Optimalidad de Dijkstra
**Si todas las aristas del laberinto tienen un costo uniforme igual a 1, ¿garantiza Dijkstra la solución con menor cantidad de pasos? ¿Qué sucedería si alguna arista tuviera peso negativo?**

**Respuesta:**  
1. **Sí, garantiza el camino más corto.** Cuando todas las aristas tienen pesos no negativos (en este caso, costo 1), Dijkstra extrae los nodos en orden no decreciente de distancia real desde el origen. Una vez que un nodo es extraído del montículo, su distancia calculada es definitiva y óptima.
2. **Aristas negativas:** Si existieran aristas con costo negativo, la propiedad de optimalidad voraz (*greedy choice property*) de Dijkstra se rompería, ya que un camino que inicialmente parecía más costoso podría volverse más económico posteriormente al sumar pesos negativos. En ese escenario, sería necesario utilizar algoritmos como Bellman-Ford o SPFA, aunque en el contexto físico de un laberinto los costos de desplazamiento siempre son positivos.

---

### Pregunta 4: Generación de Laberintos y Teoría de Árboles
**¿Qué propiedad matemática de la teoría de grafos caracteriza a un laberinto generado mediante Backtracking recursivo antes de abrirle atajos?**

**Respuesta:**  
El laberinto resultante de la primera fase de generación es un **Árbol Generador (Spanning Tree)** del grafo de casillas transitables.  
Las propiedades fundamentales de esta estructura son:
1. **Es conexo:** Existe al menos un camino para conectar cualquier par de celdas libres.
2. **Es acíclico:** No contiene ningún ciclo cerrado o bucle.
3. **Unicidad de camino:** Entre cualquier punto de inicio y cualquier punto de meta existe exactamente **una única trayectoria simple**.  
Al aplicar posteriormente la función de apertura de caminos alternativos (`caminos_alternativos=True`), se derriban muros adicionales introduciendo ciclos controlados, lo que crea múltiples caminos alternativos de diferentes longitudes para que el algoritmo de Dijkstra determine cuál es el más eficiente.

---

### Pregunta 5: Eliminación de Entradas Obsoletas en el Min-Heap
**En la implementación de `algoritmos.py`, ¿por qué se incluye la validación `if dist_actual > distancias.get(nodo_actual, float('inf'))` después de extraer un elemento del montículo?**

**Respuesta:**  
El módulo estándar `heapq` de Python no implementa la operación `decrease-key` (modificar la prioridad de un elemento existente dentro del montículo).  
Por lo tanto, cuando se encuentra un camino más corto hacia un nodo que ya estaba en el montículo, se inserta una nueva tupla `(nueva_distancia, nodo)` sin eliminar la anterior. Como consecuencia, el montículo contendrá múltiples entradas para el mismo nodo con diferentes distancias.  
La condición `if dist_actual > distancias[nodo_actual]` detecta y descarta inmediatamente las entradas obsoletas (*lazy deletion*), evitando reprocesar vecinos innecesariamente y manteniendo la complejidad del algoritmo acotada.
