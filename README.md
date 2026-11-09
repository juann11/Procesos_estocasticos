# Simulador de cadenas de Markov

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.66-FF4B4B?logo=streamlit&logoColor=white)
![Pruebas](https://img.shields.io/badge/pruebas-48%20pasando-2EA44F)

Aplicación web que analiza una cadena de Markov a partir de su matriz estocástica: determina si se alcanza un estado estable, calcula la distribución estacionaria y el **mixing time**, y contrasta la teoría con una simulación Monte Carlo.

Trabajo Final de **Procesos Estocásticos** (2026).

![Resumen de la aplicación](documentos/imagenes/resumen.png)

## Contenido

- [Funcionalidades](#funcionalidades)
- [Fundamento matemático](#fundamento-matemático)
- [Instalación](#instalación)
- [Uso](#uso)
- [Pruebas](#pruebas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Documentación](#documentación)
- [Autores](#autores)
- [Referencias](#referencias)

## Funcionalidades

El programa cubre los cinco ítems del enunciado:

| Ítem | Qué hace |
|---|---|
| 1. Entrada | Tabla editable de hasta 12 estados. Acepta decimales (`0.25` o `0,25`) y fracciones (`1/3`), y señala la casilla o la fila exacta que tiene un error. |
| 2. Estado estable | Calcula las clases comunicantes, las clases cerradas y el período, y explica por qué no hay estado estable cuando no lo hay. |
| 3. Distribución estacionaria | Calcula π y la muestra en tabla y en gráfico de barras. |
| 4. Mixing time | Calcula t<sub>mix</sub>(ε) con ε ajustable, grafica d(t) y muestra el segundo valor propio \|λ₂\|. |
| 5. Funcionalidad propia | Simulación Monte Carlo que compara la convergencia empírica con la teórica. |

Además, la interfaz incluye:

- Tarjetas de resumen con las respuestas principales.
- Mapa de calor de la matriz y grafo de transiciones.
- Animación paso a paso de la convergencia hacia π.
- Una explicación desplegable en cada sección.

| Grafo de transiciones | Animación de convergencia |
|---|---|
| ![Grafo con dos clases cerradas](documentos/imagenes/grafo.png) | ![Distribución en el paso t frente a π](documentos/imagenes/animacion.png) |

## Fundamento matemático

**Estado estable.** Una cadena finita converge a una única distribución, sin importar el estado inicial, cuando tiene exactamente **una clase cerrada** y esa clase es **aperiódica**. Los estados transitorios no impiden la convergencia.

**Distribución estacionaria.** Es la solución de

$$\pi P = \pi, \qquad \sum_i \pi_i = 1,$$

que se resuelve por mínimos cuadrados.

**Mixing time.** Con la distancia de variación total

$$\lVert \mu - \nu \rVert_{TV} = \tfrac{1}{2} \sum_x \lvert \mu(x) - \nu(x) \rvert,$$

se define la peor distancia a π después de t pasos y el primer paso en que baja de la tolerancia ε:

$$d(t) = \max_x \lVert P^t(x, \cdot) - \pi \rVert_{TV}, \qquad t_{mix}(\varepsilon) = \min\{\, t \ge 0 : d(t) \le \varepsilon \,\}.$$

Por defecto se usa ε = 1/4, con un límite de 100 000 pasos.

## Instalación

Requisitos: [uv](https://docs.astral.sh/uv/). Si no tienes Python 3.12 o superior, uv lo instala solo.

```bash
git clone https://github.com/juann11/Procesos_estocasticos.git
cd Procesos_estocasticos
uv sync
```

## Uso

```bash
uv run python -m streamlit run simulador/app.py
```

El navegador se abre en `http://localhost:8501`. En la barra lateral se elige una matriz de ejemplo o una personalizada, y la tolerancia ε. Para cambiar un valor de la matriz, haz doble clic en la casilla.

| Ejemplo | Resultado esperado |
|---|---|
| Regular (2 estados) | Converge. π = (0.8333, 0.1667), mixing time 2 |
| Regular (3 estados) | Converge. π = (0.3, 0.3, 0.4), mixing time 1 |
| Absorbente con transitorios | Converge. π = (0, 0, 1), mixing time 5 |
| Periódica (2 estados) | No converge: período 2 |
| Dos estados absorbentes | No converge: dos clases cerradas |

## Pruebas

```bash
uv run python -m pytest
```

Son 48 pruebas: 40 cubren la lógica matemática y 8 la interfaz, usando el probador de Streamlit.

## Estructura del proyecto

```
.
├── simulador/
│   ├── app.py           # Interfaz web en Streamlit
│   └── markov.py        # Lógica: validación, clases, período, π, mixing time y simulación
├── pruebas/
│   ├── test_markov.py   # Pruebas de la lógica
│   └── test_app.py      # Pruebas de la interfaz
├── documentos/
│   ├── Reporte_especificacion.docx
│   ├── Diapositivas.pdf
│   ├── Notas_del_orador.md
│   ├── Guia_de_exposicion.md
│   └── imagenes/        # Capturas usadas en este README
├── .streamlit/config.toml   # Tema y fuentes de la interfaz
└── pyproject.toml
```

La lógica (`markov.py`) no depende de la interfaz, así que se prueba por separado.

## Documentación

- [Reporte de especificación](documentos/Reporte_especificacion.docx)
- [Diapositivas](documentos/Diapositivas.pdf)
- [Notas del orador](documentos/Notas_del_orador.md)
- [Guía de exposición](documentos/Guia_de_exposicion.md)

## Autores

- Juan José Ospina
- Geronimo Gaviria

## Referencias

- Levin, D. A., Peres, Y. y Wilmer, E. L. *Markov Chains and Mixing Times*, 2.ª ed. American Mathematical Society, 2017.
