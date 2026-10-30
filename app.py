"""Interfaz del simulador de cadenas de Markov."""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from markov import (
    analizar_cadena,
    distancia_tv,
    distribucion_estacionaria,
    evolucion_exacta,
    mixing_time,
    simular,
    validar_matriz,
)

PERSONALIZADA = "Personalizada"
EJEMPLOS = {
    "Regular (2 estados)": [[0.9, 0.1], [0.5, 0.5]],
    "Regular (3 estados)": [[0.2, 0.5, 0.3], [0.4, 0.1, 0.5], [0.3, 0.3, 0.4]],
    "Absorbente con transitorios": [[0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.0, 0.0, 1.0]],
    "Periódica (2 estados)": [[0.0, 1.0], [1.0, 0.0]],
    "Dos estados absorbentes": [[1.0, 0.0, 0.0], [0.3, 0.4, 0.3], [0.0, 0.0, 1.0]],
    PERSONALIZADA: None,
}
AZUL = "#2a78d6"
NARANJA = "#eb6834"
MAX_PUNTOS_GRAFICA = 2000


def nombres(estados):
    return ", ".join(f"E{i + 1}" for i in estados)


def grafica_distancias(datos: pd.DataFrame, epsilon: float | None = None) -> alt.LayerChart:
    series = list(datos["Serie"].unique())
    base = alt.Chart(datos).encode(
        x=alt.X("Paso:Q", title="Paso t", axis=alt.Axis(tickMinStep=1, format="d")),
        y=alt.Y("Distancia:Q", title="Distancia a π", scale=alt.Scale(domainMin=0)),
        color=alt.Color(
            "Serie:N",
            scale=alt.Scale(domain=series, range=[AZUL, NARANJA][: len(series)]),
            legend=alt.Legend(orient="top", title=None) if len(series) > 1 else None,
        ),
    )
    capas = [
        base.mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=40, filled=True)).encode(
            tooltip=["Serie:N", "Paso:Q", alt.Tooltip("Distancia:Q", format=".4f")]
        ),
    ]
    if epsilon is not None:
        linea = alt.Chart(pd.DataFrame({"ε": [epsilon]}))
        capas.append(linea.mark_rule(strokeDash=[6, 4], color="#475569").encode(y="ε:Q"))
    return alt.layer(*capas).properties(height=300)


def recortar(datos: pd.DataFrame) -> pd.DataFrame:
    # shortcut: submuestrea filas parejo, puede saltarse el último punto de cadenas muy lentas
    paso = max(1, len(datos) // MAX_PUNTOS_GRAFICA)
    return datos.iloc[::paso]


st.set_page_config(page_title="Simulador de cadenas de Markov", layout="centered")
st.title("Simulador de cadenas de Markov")
st.caption("Distribución estacionaria y mixing time. Procesos Estocásticos, Trabajo Final.")

# Ítem 1: entrada
st.header("1. Matriz estocástica")
ejemplo = st.selectbox("Matriz de partida", list(EJEMPLOS), key="ejemplo")
if ejemplo == PERSONALIZADA:
    n = st.number_input("Número de estados", min_value=2, max_value=12, value=3)
    inicial = np.full((n, n), 1 / n)
else:
    inicial = np.array(EJEMPLOS[ejemplo])
    n = len(inicial)

etiquetas = [f"E{i + 1}" for i in range(n)]
st.caption(
    "Cada fila es el estado actual, cada columna el siguiente. Cada fila debe sumar 1. "
    "Para cambiar un valor, haz doble clic en la casilla."
)
editada = st.data_editor(
    pd.DataFrame(inicial, index=etiquetas, columns=etiquetas),
    key=f"matriz-{ejemplo}-{n}",
    width="stretch",
)
P = editada.to_numpy(dtype=float)

errores = validar_matriz(P)
if errores:
    for error in errores:
        st.error(error)
    st.stop()

# Ítem 2: convergencia
st.header("2. ¿Se alcanza un estado estable?")
analisis = analizar_cadena(P)
cerradas = len(analisis.clases_cerradas)
if analisis.converge:
    st.success("Sí, se alcanza: hay una única clase cerrada y es aperiódica.")
elif cerradas > 1:
    lista = "; ".join(f"{{{nombres(c)}}}" for c in analisis.clases_cerradas)
    st.warning(
        f"No se alcanza: hay {cerradas} clases cerradas ({lista}), "
        "así que el resultado depende del estado inicial."
    )
else:
    st.warning(
        f"No se alcanza: la clase cerrada tiene período {analisis.periodo}, "
        "así que la cadena oscila y no se estabiliza."
    )
st.write("**Clases comunicantes:** " + " · ".join(f"{{{nombres(c)}}}" for c in analisis.clases))
transitorios = [c for c in analisis.clases if c not in analisis.clases_cerradas]
if transitorios:
    st.write("**Clases transitorias:** " + " · ".join(f"{{{nombres(c)}}}" for c in transitorios))
if not analisis.converge:
    st.stop()

# Ítem 3: estado estable
st.header("3. Distribución de estado estable")
pi = distribucion_estacionaria(P)
tabla_pi = pd.DataFrame({"Estado": etiquetas, "π": pi})
izquierda, derecha = st.columns([1, 2])
izquierda.dataframe(tabla_pi.round(4), hide_index=True, width="stretch")
derecha.altair_chart(
    alt.Chart(tabla_pi)
    .mark_bar(color=AZUL, cornerRadiusEnd=4, size=28)
    .encode(
        x=alt.X("Estado:N", sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("π:Q", scale=alt.Scale(domain=[0, 1])),
        tooltip=["Estado:N", alt.Tooltip("π:Q", format=".4f")],
    )
    .properties(height=220),
    width="stretch",
)

# Ítem 4: mixing time
st.header("4. Mixing time")
epsilon = st.number_input(
    "Tolerancia ε", min_value=0.001, max_value=0.5, value=0.25, step=0.01, format="%.3f"
)
mezcla = mixing_time(P, epsilon)
if mezcla.t_mix is None:
    st.warning(f"No se alcanzó ε en {len(mezcla.distancias) - 1:,} pasos: la cadena mezcla muy lento.")
else:
    st.metric(f"Mixing time para ε = {epsilon:g}", mezcla.t_mix, help="Pasos hasta que d(t) ≤ ε")
curva = pd.DataFrame(
    {"Paso": range(len(mezcla.distancias)), "Distancia": mezcla.distancias, "Serie": "d(t)"}
)
st.altair_chart(grafica_distancias(recortar(curva), epsilon), width="stretch")
st.caption("d(t) es la peor distancia de variación total entre todos los estados iniciales. La línea punteada es ε.")

# Ítem 5: funcionalidad particular
st.header("5. Simulación Monte Carlo")
st.write("Lanza caminantes por la cadena y compara lo observado con la teoría.")
col1, col2, col3 = st.columns(3)
inicio = col1.selectbox("Estado inicial", etiquetas)
caminantes = col2.select_slider("Caminantes", [100, 1000, 10_000, 100_000], value=10_000)
sugeridos = max(20, 2 * (mezcla.t_mix or 100))
pasos = col3.number_input("Pasos", min_value=1, max_value=1000, value=min(sugeridos, 1000))

estado = etiquetas.index(inicio)
empirica = simular(P, estado, caminantes, pasos, semilla=42)
exacta = evolucion_exacta(P, estado, pasos)
comparacion = pd.concat(
    pd.DataFrame({"Paso": range(pasos + 1), "Distancia": distancia_tv(filas, pi, axis=1), "Serie": serie})
    for filas, serie in ((exacta, "Teórica"), (empirica, "Simulada"))
)
st.altair_chart(grafica_distancias(comparacion), width="stretch")
st.caption("La curva simulada se estanca en un nivel de ruido; al subir los caminantes se acerca a la teórica.")
st.dataframe(
    pd.DataFrame({"Estado": etiquetas, "π teórica": pi, "Simulada (último paso)": empirica[-1]}).round(4),
    hide_index=True,
    width="stretch",
)
