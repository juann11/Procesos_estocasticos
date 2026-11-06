"""Interfaz del simulador de cadenas de Markov."""
import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from markov import (
    analizar_cadena,
    distancia_tv,
    distribucion_estacionaria,
    evolucion_exacta,
    grafo_dot,
    leer_matriz,
    mixing_time,
    segundo_valor_propio,
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
GRIS = "#475569"
MAX_PUNTOS_GRAFICA = 2000
MAX_ESTADOS_GRAFO = 8  # con más estados las flechas se vuelven ilegibles
INTEGRANTES = "Juan José Ospina y Geronimo Gaviria"


def nombres(estados):
    return ", ".join(f"E{i + 1}" for i in estados)


def explicar(texto: str):
    with st.expander("¿Qué significa?"):
        st.markdown(texto)


def grafica_distancias(datos: pd.DataFrame, epsilon=None, t_mix=None) -> alt.LayerChart:
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
        capas.append(linea.mark_rule(strokeDash=[6, 4], color=GRIS).encode(y="ε:Q"))
    if t_mix is not None:
        marca = alt.Chart(pd.DataFrame({"t": [t_mix], "texto": [f"t_mix = {t_mix}"]}))
        capas.append(marca.mark_rule(color=NARANJA, strokeWidth=2).encode(x="t:Q"))
        capas.append(
            marca.mark_text(align="right", dx=-6, dy=-120, color=NARANJA, fontWeight="bold", fontSize=13)
            .encode(x="t:Q", text="texto:N")
        )
    return alt.layer(*capas).properties(height=320)


def mapa_de_calor(P, etiquetas) -> alt.LayerChart:
    datos = pd.DataFrame(
        [(etiquetas[i], etiquetas[j], P[i, j]) for i in range(len(P)) for j in range(len(P))],
        columns=["Desde", "Hacia", "Probabilidad"],
    )
    base = alt.Chart(datos).encode(
        x=alt.X("Hacia:N", sort=etiquetas, axis=alt.Axis(orient="top", labelAngle=0, title="Hacia")),
        y=alt.Y("Desde:N", sort=etiquetas, title="Desde"),
    )
    celdas = base.mark_rect(stroke="#F8FAFC", strokeWidth=2).encode(
        color=alt.Color("Probabilidad:Q", scale=alt.Scale(domain=[0, 1], scheme="blues"), legend=None),
        tooltip=["Desde:N", "Hacia:N", alt.Tooltip("Probabilidad:Q", format=".4f")],
    )
    texto = base.mark_text(fontSize=13).encode(
        text=alt.Text("Probabilidad:Q", format=".2f"),
        color=alt.condition("datum.Probabilidad > 0.55", alt.value("#F8FAFC"), alt.value("#0F172A")),
    )
    return (celdas + texto).properties(height=alt.Step(44))


def grafica_paso(distribucion, pi, etiquetas) -> alt.Chart:
    series = ["Distribución en el paso t", "π (estado estable)"]
    datos = pd.DataFrame(
        {
            "Estado": etiquetas * 2,
            "Serie": [series[0]] * len(etiquetas) + [series[1]] * len(etiquetas),
            "Probabilidad": np.concatenate([distribucion, pi]),
        }
    )
    return (
        alt.Chart(datos)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("Estado:N", sort=etiquetas, axis=alt.Axis(labelAngle=0)),
            xOffset=alt.XOffset("Serie:N", sort=series),
            y=alt.Y("Probabilidad:Q", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color(
                "Serie:N",
                scale=alt.Scale(domain=series, range=[AZUL, NARANJA]),
                legend=alt.Legend(orient="top", title=None),
            ),
            tooltip=["Estado:N", "Serie:N", alt.Tooltip("Probabilidad:Q", format=".4f")],
        )
        .properties(height=300)
    )


def recortar(datos: pd.DataFrame) -> pd.DataFrame:
    # shortcut: submuestrea filas parejo, puede saltarse el último punto de cadenas muy lentas
    paso = max(1, len(datos) // MAX_PUNTOS_GRAFICA)
    return datos.iloc[::paso]


def pie_de_pagina():
    st.divider()
    st.caption(f"{INTEGRANTES} · Procesos Estocásticos · Trabajo Final 2026")


st.set_page_config(page_title="Simulador de cadenas de Markov", layout="wide")

# Barra lateral: lo que se elige antes de calcular
with st.sidebar:
    st.header("Configuración")
    ejemplo = st.selectbox("Matriz de partida", list(EJEMPLOS), key="ejemplo")
    if ejemplo == PERSONALIZADA:
        n = st.number_input("Número de estados", min_value=2, max_value=12, value=3)
    else:
        n = len(EJEMPLOS[ejemplo])
    epsilon = st.number_input(
        "Tolerancia ε del mixing time", min_value=0.001, max_value=0.5, value=0.25, step=0.01, format="%.3f"
    )
    st.divider()
    st.markdown(
        "**Cómo usar**\n\n"
        "1. Elige un ejemplo o una matriz personalizada.\n"
        "2. Haz doble clic en una casilla para cambiarla.\n"
        "3. Acepta decimales (0.25 o 0,25) y fracciones (1/3)."
    )

st.title("Simulador de cadenas de Markov")
st.caption("Distribución estacionaria y mixing time · Procesos Estocásticos, Trabajo Final")
resumen = st.container()

# Ítem 1: entrada
st.header("1. Matriz estocástica")
inicial = np.full((n, n), f"1/{n}") if ejemplo == PERSONALIZADA else np.array(EJEMPLOS[ejemplo]).astype(str)
etiquetas = [f"E{i + 1}" for i in range(n)]
columna_tabla, columna_mapa = st.columns([3, 2], gap="large")
with columna_tabla:
    st.caption("Cada fila es el estado actual y cada columna el siguiente. Cada fila debe sumar 1.")
    editada = st.data_editor(
        pd.DataFrame(inicial, index=etiquetas, columns=etiquetas),
        key=f"matriz-{ejemplo}-{n}",
        width="stretch",
    )
P, errores = leer_matriz(editada.to_numpy().tolist())
errores = errores or validar_matriz(P)
if errores:
    for error in errores:
        columna_tabla.error(error)
    pie_de_pagina()
    st.stop()
with columna_mapa:
    st.caption("Mapa de calor: entre más oscuro, más probable la transición.")
    st.altair_chart(mapa_de_calor(P, etiquetas), width="stretch")
explicar(
    "P(i, j) es la probabilidad de pasar del estado i al estado j en un paso. "
    "Por eso ningún valor puede ser negativo y cada fila debe sumar 1: desde cualquier estado, "
    "la cadena tiene que ir a alguna parte."
)

# Ítem 2: convergencia
st.header("2. ¿Se alcanza un estado estable?")
analisis = analizar_cadena(P)
cerradas = len(analisis.clases_cerradas)
columna_texto, columna_grafo = st.columns([3, 2], gap="large")
with columna_texto:
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
    st.markdown("**Clases comunicantes:** " + " · ".join(f"{{{nombres(c)}}}" for c in analisis.clases))
    st.markdown("**Clases cerradas:** " + " · ".join(f"{{{nombres(c)}}}" for c in analisis.clases_cerradas))
    transitorios = [c for c in analisis.clases if c not in analisis.clases_cerradas]
    if transitorios:
        st.markdown("**Clases transitorias:** " + " · ".join(f"{{{nombres(c)}}}" for c in transitorios))
if n <= MAX_ESTADOS_GRAFO:
    with columna_grafo:
        st.graphviz_chart(grafo_dot(P, analisis.clases_cerradas))
        st.caption("Doble círculo y relleno azul: estados de clases cerradas. Flechas más gruesas: más probables.")
explicar(
    "La cadena llega a un único estado estable, sin importar dónde empiece, cuando tiene "
    "**exactamente una clase cerrada** (un grupo del que no puede salir) y esa clase es **aperiódica**. "
    "El período es el MCD de las longitudes de los ciclos: si es 2 o más, la cadena oscila. "
    "Los estados transitorios no estorban, porque la cadena termina abandonándolos."
)

with resumen:
    if analisis.converge:
        pi = distribucion_estacionaria(P)
        mezcla = st.cache_data(mixing_time, show_spinner="Calculando el mixing time…")(P, epsilon)
        tarjetas = st.columns(4)
        tarjetas[0].metric("¿Estado estable?", "Sí", border=True)
        tarjetas[1].metric(
            "Mixing time",
            "No alcanzó" if mezcla.t_mix is None else mezcla.t_mix,
            help=f"Pasos hasta que d(t) ≤ ε = {epsilon:g}",
            border=True,
        )
        tarjetas[2].metric(
            "|λ₂|",
            f"{segundo_valor_propio(P):.4f}",
            help="d(t) decae aproximadamente como |λ₂|^t: entre más cerca de 1, más lenta la mezcla.",
            border=True,
        )
        tarjetas[3].metric(
            "Estado más probable",
            etiquetas[int(np.argmax(pi))],
            help=f"π = {pi.max():.4f} a largo plazo",
            border=True,
        )
    else:
        tarjetas = st.columns(3)
        tarjetas[0].metric("¿Estado estable?", "No", border=True)
        tarjetas[1].metric("Clases cerradas", cerradas, border=True)
        tarjetas[2].metric("Período", "—" if analisis.periodo is None else analisis.periodo, border=True)

if not analisis.converge:
    pie_de_pagina()
    st.stop()

# Ítem 3: estado estable
st.header("3. Distribución de estado estable")
tabla_pi = pd.DataFrame({"Estado": etiquetas, "π": pi})
izquierda, derecha = st.columns([1, 2], gap="large")
izquierda.dataframe(tabla_pi.round(4), hide_index=True, width="stretch")
barras = alt.Chart(tabla_pi).encode(
    x=alt.X("Estado:N", sort=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("π:Q", scale=alt.Scale(domain=[0, 1])),
)
derecha.altair_chart(
    (
        barras.mark_bar(color=AZUL, cornerRadiusEnd=4, size=32).encode(
            tooltip=["Estado:N", alt.Tooltip("π:Q", format=".4f")]
        )
        + barras.mark_text(dy=-10, fontSize=13, color="#0F172A").encode(text=alt.Text("π:Q", format=".4f"))
    ).properties(height=240),
    width="stretch",
)
explicar(
    "π es la distribución que no cambia al aplicar P: πP = π, con la condición de que sume 1. "
    "Es el reparto de probabilidad al que llega la cadena a largo plazo. "
    "Se calcula resolviendo ese sistema lineal por mínimos cuadrados."
)

# Ítem 4: mixing time
st.header("4. Mixing time")
st.caption(f"ε = {epsilon:g}. Puedes cambiarlo en la barra lateral.")
if mezcla.t_mix is None:
    st.warning(f"No se alcanzó ε en {len(mezcla.distancias) - 1:,} pasos: la cadena mezcla muy lento.")
distancias = mezcla.distancias
if mezcla.t_mix is not None:
    # Con ε = 0 la curva sigue después de t_mix y se ve que continúa bajando
    distancias = st.cache_data(mixing_time)(P, 0.0, max(10, 2 * mezcla.t_mix)).distancias
curva = pd.DataFrame({"Paso": range(len(distancias)), "Distancia": distancias, "Serie": "d(t)"})
st.altair_chart(grafica_distancias(recortar(curva), epsilon, mezcla.t_mix), width="stretch")
st.caption("d(t) es la peor distancia de variación total entre todos los estados iniciales. La línea punteada es ε.")
explicar(
    "El mixing time mide cuántos pasos necesita la cadena para olvidar su estado inicial, es decir, "
    "para quedar lo bastante cerca de π sin importar dónde empezó. En cada paso t se compara cada fila "
    "de Pᵗ con π usando la distancia de variación total, ½ Σ |μ(x) − π(x)|, y se toma el peor caso: d(t). "
    "El mixing time es el primer t con d(t) ≤ ε. |λ₂| explica la velocidad: d(t) decae aproximadamente como |λ₂|ᵗ."
)

st.subheader("Animación de convergencia")
st.caption("Mira cómo la distribución desde un estado inicial se va pareciendo a π, paso a paso.")
limite_animacion = 30 if mezcla.t_mix is None else min(max(10, 3 * mezcla.t_mix), 60)
control_inicio, control_paso, control_boton = st.columns([1, 3, 1], vertical_alignment="bottom")
inicio_animacion = control_inicio.selectbox("Estado inicial", etiquetas, key="animacion_inicio")
paso_elegido = control_paso.slider("Paso t", 0, limite_animacion, 0, key="paso_animacion")
reproducir = control_boton.button("▶ Reproducir", width="stretch")
evolucion = evolucion_exacta(P, etiquetas.index(inicio_animacion), limite_animacion)
lienzo = st.empty()


def dibujar_paso(t: int):
    with lienzo.container():
        st.altair_chart(grafica_paso(evolucion[t], pi, etiquetas), width="stretch")
        st.caption(f"En t = {t} la distancia a π es {distancia_tv(evolucion[t], pi):.4f}")


if reproducir:
    for t in range(limite_animacion + 1):
        dibujar_paso(t)
        time.sleep(0.4)
else:
    dibujar_paso(paso_elegido)

# Ítem 5: funcionalidad particular
st.header("5. Simulación Monte Carlo")
st.write("Lanza caminantes por la cadena y compara lo observado con la teoría.")
col1, col2, col3 = st.columns(3)
inicio = col1.selectbox("Estado inicial", etiquetas, key="simulacion_inicio")
caminantes = col2.select_slider("Caminantes", [100, 1000, 10_000, 100_000], value=10_000)
sugeridos = 200 if mezcla.t_mix is None else max(20, 2 * mezcla.t_mix)
pasos = col3.number_input("Pasos", min_value=1, max_value=1000, value=min(sugeridos, 1000))

estado = etiquetas.index(inicio)
empirica = st.cache_data(simular, show_spinner="Simulando…")(P, estado, caminantes, pasos, semilla=42)
exacta = evolucion_exacta(P, estado, pasos)
comparacion = pd.concat(
    pd.DataFrame({"Paso": range(pasos + 1), "Distancia": distancia_tv(filas, pi, axis=1), "Serie": serie})
    for filas, serie in ((exacta, "Teórica"), (empirica, "Simulada"))
)
grafica_simulacion, tabla_simulacion = st.columns([2, 1], gap="large")
grafica_simulacion.altair_chart(grafica_distancias(comparacion), width="stretch")
tabla_simulacion.dataframe(
    pd.DataFrame({"Estado": etiquetas, "π teórica": pi, "Simulada (último paso)": empirica[-1]}).round(4),
    hide_index=True,
    width="stretch",
)
st.caption("La curva simulada se estanca en un nivel de ruido; al subir los caminantes se acerca a la teórica.")
explicar(
    "Cada caminante arranca en el estado inicial y en cada paso sortea un número u entre 0 y 1: "
    "el tramo de la fila acumulada de P donde cae u decide su siguiente estado. "
    "Contando cuántos caminantes hay en cada estado se obtiene una distribución empírica, "
    "que se compara con la teórica. Es una verificación independiente del álgebra; "
    "el ruido baja como 1/√N, así que 10 veces más caminantes lo reducen unas 3 veces."
)

pie_de_pagina()
