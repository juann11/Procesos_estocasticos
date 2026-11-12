"""Experimento: ¿cuántas veces hay que barajar un mazo para que quede bien mezclado?"""
from collections import defaultdict
from math import factorial

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from markov import (
    analizar_cadena,
    barajadas_equivalentes,
    distancia_barajado,
    distancia_tv,
    distribucion_subidas,
    eulerianos,
    leer_experimento,
    matriz_riffle,
    mixing_time,
    subidas,
)

AZUL = "#2a78d6"
NARANJA = "#eb6834"
GRIS = "#475569"
EPSILON = 0.25
MAX_BARAJADAS = 12


def en_resumen(texto: str):
    st.info(f"**En resumen:** {texto}", icon=":material/lightbulb:")


st.set_page_config(page_title="Experimento: barajar cartas", layout="wide")
st.title("Experimento: ¿cuántas veces hay que barajar?")
st.caption(
    "Barajar un mazo es una cadena de Markov: cada barajada cambia el orden de las cartas al azar. "
    "El mixing time responde cuántas barajadas hacen falta para que el mazo quede bien mezclado."
)

with st.expander("¿Cómo se conecta con el taller?", expanded=True):
    st.markdown(
        "Cada **estado** es un orden posible del mazo y cada **paso** es una barajada tipo *riffle*: se corta el "
        "mazo en dos montones y se entrelazan. Usamos el modelo de Gilbert, Shannon y Reeds, que describe ese riffle.\n\n"
        "1. **Matriz estocástica:** para un mazo pequeño se construye completa, con un estado por cada orden.\n"
        "2. **¿Estado estable?** Se aplica el mismo criterio del simulador.\n"
        "3. **Distribución estacionaria:** todos los órdenes igual de probables, es decir, un mazo bien mezclado.\n"
        "4. **Mixing time:** cuántas barajadas hacen falta.\n"
        "5. **Experimento propio:** barajamos un mazo real y comparamos nuestras barajadas con el modelo."
    )

# 1. Mazo pequeño: la matriz completa con el mismo simulador
st.header("1. Un mazo pequeño como cadena de Markov")
n_pequeno = st.number_input("Cartas del mazo pequeño", min_value=3, max_value=5, value=4, key="mazo_pequeno")
P, ordenes = matriz_riffle(n_pequeno)
analisis = analizar_cadena(P)
mezcla = mixing_time(P, EPSILON)
uniforme = 1 / factorial(n_pequeno)
pi_pequeno = np.full(len(ordenes), uniforme)
pequeno = st.columns(4)
pequeno[0].metric("Órdenes posibles (estados)", len(ordenes), border=True)
pequeno[1].metric("¿Estado estable?", "Sí" if analisis.converge else "No", border=True)
pequeno[2].metric("Probabilidad de cada orden (π)", f"1/{len(ordenes)}", border=True)
pequeno[3].metric("Barajadas para mezclar", mezcla.t_mix, help=f"Mixing time con ε = {EPSILON:g}", border=True)
st.markdown(
    f"La matriz tiene {len(ordenes)} × {len(ordenes)} entradas. Desde cualquier orden, un riffle deja el mazo igual "
    f"con probabilidad {n_pequeno + 1}/{2 ** n_pequeno} y lleva a cada orden con dos secuencias ascendentes con "
    f"probabilidad 1/{2 ** n_pequeno}. El simulador encuentra una sola clase cerrada y aperiódica, y π reparte la "
    "probabilidad por igual entre todos los órdenes."
)
en_resumen(
    f"con {n_pequeno} cartas basta con {mezcla.t_mix} barajadas para que cualquier orden sea casi igual de probable."
)

# 2. Mazo completo: fórmula exacta de Bayer y Diaconis
st.header("2. Un mazo de 52 cartas")
distancias_52 = [distancia_barajado(52, k) for k in range(1, MAX_BARAJADAS + 1)]
t_mix_52 = next(k for k, d in enumerate(distancias_52, 1) if d <= EPSILON)
completo = st.columns(3)
completo[0].metric("Órdenes posibles", "52! ≈ 8 × 10⁶⁷", border=True)
completo[1].metric("Barajadas para mezclar 52 cartas", t_mix_52, help=f"Mixing time con ε = {EPSILON:g}", border=True)
completo[2].metric("Distancia tras 7 barajadas", f"{distancias_52[6]:.3f}", border=True)
st.caption(
    "Con 52 cartas hay demasiados órdenes para armar la matriz, así que usamos la fórmula exacta de Bayer y Diaconis "
    "(1992), que en el mazo pequeño coincide con lo que calcula nuestro simulador."
)
curva_52 = pd.DataFrame({"Barajadas": range(1, MAX_BARAJADAS + 1), "Distancia": distancias_52})
st.altair_chart(
    alt.Chart(curva_52).mark_line(point=True, color=AZUL).encode(
        x=alt.X("Barajadas:Q", axis=alt.Axis(tickMinStep=1, format="d")),
        y=alt.Y("Distancia:Q", title="Distancia a un mazo bien mezclado", scale=alt.Scale(domain=[0, 1])),
        tooltip=["Barajadas:Q", alt.Tooltip("Distancia:Q", format=".3f")],
    )
    + alt.Chart(pd.DataFrame({"ε": [EPSILON]})).mark_rule(strokeDash=[6, 4], color=GRIS).encode(y="ε:Q"),
    width="stretch",
)
en_resumen(
    "hasta la cuarta barajada el mazo sigue casi en orden y entre la quinta y la octava se mezcla de golpe. "
    f"Con 52 cartas hacen falta {t_mix_52} barajadas para bajar de ε = {EPSILON:g}; el famoso «7 barajadas» "
    "sale de ese salto."
)

# 3. Experimento con un mazo real
st.header("3. Nuestro experimento: ¿barajamos como el modelo?")
st.markdown(
    "1. Tomen **n cartas numeradas del 1 al n**, ordenadas de arriba abajo (por ejemplo, del as al 10).\n"
    "2. Háganles **k barajadas tipo riffle**: cortar en dos montones y entrelazarlos.\n"
    "3. Escriban el orden de arriba abajo, una línea por intento: `barajadas: orden`.\n"
    "4. Vuelvan a ordenar el mazo y repitan. Entre más intentos, más confiable el resultado."
)
texto = st.text_area(
    "Resultados del experimento",
    key="experimento",
    height=180,
    placeholder="1: 6 1 7 2 8 3 9 4 10 5\n2: 3 8 1 6 9 4 2 10 7 5",
)
ensayos, errores = leer_experimento(texto)
if errores:
    for error in errores:
        st.error(error)
    st.stop()
if not ensayos:
    st.info("Cuando escriban sus resultados aquí, la app los compara con el modelo.", icon=":material/style:")
    st.stop()

n = len(ensayos[0][1])
por_barajadas = defaultdict(list)
for k, orden in ensayos:
    por_barajadas[k].append(subidas(orden))

filas = []
for k in sorted(por_barajadas):
    observada = np.bincount(por_barajadas[k], minlength=n + 1)[1:] / len(por_barajadas[k])
    filas.append(
        {
            "Barajadas reales": k,
            "Intentos": len(por_barajadas[k]),
            "Distancia al modelo": distancia_tv(observada, distribucion_subidas(n, k)),
            "Equivalen a barajadas del modelo": barajadas_equivalentes(observada, n),
        }
    )
resultados = pd.DataFrame(filas)
st.dataframe(resultados.round(3), hide_index=True, width="stretch")
for fila in filas:
    st.markdown(
        f"- Sus **{fila['Barajadas reales']}** barajadas reales equivalen a unas "
        f"**{fila['Equivalen a barajadas del modelo']}** barajadas del modelo ({fila['Intentos']} intentos)."
    )

k_elegido = st.selectbox("Ver el detalle de", sorted(por_barajadas), format_func=lambda k: f"{k} barajadas")
observada = np.bincount(por_barajadas[k_elegido], minlength=n + 1)[1:] / len(por_barajadas[k_elegido])
comparacion = pd.DataFrame(
    {
        "Secuencias ascendentes": list(range(1, n + 1)) * 2,
        "Fuente": ["Nuestro experimento"] * n + ["Modelo"] * n,
        "Proporción": np.concatenate([observada, distribucion_subidas(n, k_elegido)]),
    }
)
st.altair_chart(
    alt.Chart(comparacion).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("Secuencias ascendentes:O", axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("Fuente:N", sort=["Nuestro experimento", "Modelo"]),
        y=alt.Y("Proporción:Q"),
        color=alt.Color("Fuente:N", scale=alt.Scale(domain=["Nuestro experimento", "Modelo"], range=[NARANJA, AZUL]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=["Secuencias ascendentes:O", "Fuente:N", alt.Tooltip("Proporción:Q", format=".3f")],
    ),
    width="stretch",
)
st.caption(
    "Una secuencia ascendente es un tramo de cartas consecutivas (1, 2, 3…) que siguen en orden de arriba abajo. "
    "Un mazo recién ordenado tiene 1; uno bien mezclado tiene cerca de la mitad del total de cartas. "
    f"Con pocas barajadas el modelo predice pocas secuencias; en un mazo uniforme de {n} cartas el promedio es "
    f"{float(np.dot(range(1, n + 1), np.array(eulerianos(n)) / factorial(n))):.1f}."
)
en_resumen(
    "si sus barajadas «equivalen» a menos barajadas del modelo, es porque al entrelazar las cartas caen en grupos y no "
    "una por una, así que el mazo se mezcla más despacio. Con pocos intentos el resultado varía bastante."
)
