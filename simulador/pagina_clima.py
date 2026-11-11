"""Caso real: cadena de Markov estimada con la lluvia diaria de Medellín."""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from markov import (
    analizar_cadena,
    clasificar_lluvia,
    distribucion_estacionaria,
    estimar_matriz,
    frecuencia_a_k_pasos,
    mixing_time,
    segundo_valor_propio,
)

DATOS = Path(__file__).parent.parent / "datos" / "clima_medellin.csv"
ESTADOS = ["Seco", "Lluvia ligera", "Lluvia fuerte"]
COLORES = ["#E9A15B", "#2a78d6", "#1E3A5F"]
AZUL = "#2a78d6"
NARANJA = "#eb6834"
DIAS_COMPARACION = 10


def en_resumen(texto: str):
    st.info(f"**En resumen:** {texto}", icon=":material/lightbulb:")

st.set_page_config(page_title="Caso real: clima de Medellín", layout="wide")
st.title("Caso real: el clima de Medellín")
st.caption(
    "¿En cuántos días se olvida el clima de hoy? Lluvia diaria de Medellín del 1 de enero de 2023 "
    "al 31 de diciembre de 2025, de la API de clima histórico de Open-Meteo."
)

with st.expander("¿Cómo se conecta con el taller?", expanded=True):
    st.markdown(
        "En el simulador la matriz P la escribe el usuario. Aquí **la estimamos con datos reales** y "
        "aplicamos los mismos cinco ítems del enunciado a una pregunta concreta:\n\n"
        "1. **Matriz estocástica:** cada día es un estado (seco, lluvia ligera o lluvia fuerte) y P se "
        "estima contando cuántas veces un tipo de día fue seguido por otro.\n"
        "2. **¿Estado estable?** Se aplica el mismo criterio: una clase cerrada y aperiódica.\n"
        "3. **Distribución estacionaria:** π dice qué proporción de días de cada tipo tiene Medellín a "
        "largo plazo, y se compara con la frecuencia real.\n"
        "4. **Mixing time:** cuántos días pasan hasta que saber cómo estuvo hoy ya no ayuda a predecir.\n"
        "5. **Validación:** se compara lo que predice la cadena con lo que pasó de verdad días después."
    )

datos = pd.read_csv(DATOS, parse_dates=["fecha"])

st.header("1. Del dato a los estados")
umbral_ligera, umbral_fuerte, tolerancia = st.columns(3)
ligera = umbral_ligera.number_input(
    "Lluvia ligera desde (mm)", min_value=0.1, max_value=20.0, value=1.0, step=0.5, key="umbral_ligera"
)
fuerte = umbral_fuerte.number_input(
    "Lluvia fuerte desde (mm)", min_value=ligera + 0.5, max_value=100.0, value=10.0, step=1.0, key="umbral_fuerte"
)
epsilon = tolerancia.number_input(
    "Tolerancia ε", min_value=0.001, max_value=0.5, value=0.25, step=0.01, format="%.3f"
)
st.caption(
    f"Un día es seco con menos de {ligera:g} mm, de lluvia ligera hasta {fuerte:g} mm y de lluvia fuerte desde ahí. "
    "1 mm es el umbral usual de día con lluvia; 10 mm, el de lluvia fuerte."
)

datos["estado"] = clasificar_lluvia(datos["lluvia_mm"], ligera, fuerte)
datos["Tipo de día"] = [ESTADOS[e] for e in datos["estado"]]
st.altair_chart(
    alt.Chart(datos)
    .mark_bar()
    .encode(
        x=alt.X("fecha:T", title=None),
        y=alt.Y("lluvia_mm:Q", title="Lluvia (mm)"),
        color=alt.Color(
            "Tipo de día:N", scale=alt.Scale(domain=ESTADOS, range=COLORES), legend=alt.Legend(orient="top", title=None)
        ),
        tooltip=[alt.Tooltip("fecha:T", format="%d/%m/%Y"), "lluvia_mm:Q", "Tipo de día:N"],
    )
    .properties(height=220),
    width="stretch",
)
en_resumen("cada uno de los días de estos tres años se convirtió en un tipo de día: seco, lluvia ligera o lluvia fuerte.")

try:
    P, conteos = estimar_matriz(datos["estado"].to_numpy(), 3)
except ValueError:
    st.error("Con estos umbrales hay un tipo de día sin datos, así que su fila de P no se puede estimar. Ajusta los umbrales.")
    st.stop()

analisis = analizar_cadena(P)
pi = distribucion_estacionaria(P)
frecuencia = np.bincount(datos["estado"], minlength=3) / len(datos)
mezcla = mixing_time(P, epsilon)

resumen = st.columns(4)
resumen[0].metric("Días analizados", len(datos), border=True)
resumen[1].metric("Días secos a largo plazo", f"{100 * pi[0]:.1f} %", border=True)
resumen[2].metric(
    "Mixing time",
    "No alcanzó" if mezcla.t_mix is None else f"{mezcla.t_mix} días",
    help=f"Días hasta que el clima de hoy deja de importar, con ε = {epsilon:g}",
    border=True,
)
resumen[3].metric("|λ₂|", f"{segundo_valor_propio(P):.3f}", border=True)

st.header("2. Matriz P estimada (ítem 1)")
izquierda, derecha = st.columns(2, gap="large")
izquierda.caption("Transiciones contadas: cuántas veces un día de la fila fue seguido por uno de la columna.")
izquierda.dataframe(pd.DataFrame(conteos, index=ESTADOS, columns=ESTADOS), width="stretch")
derecha.caption("P: cada fila dividida entre su total. Cada fila suma 1.")
derecha.dataframe(pd.DataFrame(P, index=ESTADOS, columns=ESTADOS).round(3), width="stretch")
st.markdown(
    f"Ejemplo de lectura: después de un día de lluvia fuerte, el día siguiente fue también de lluvia fuerte "
    f"el **{100 * P[2, 2]:.1f} %** de las veces, y seco solo el **{100 * P[2, 0]:.1f} %**."
)
en_resumen(
    "la matriz dice qué tan probable es cada tipo de día mañana según cómo fue hoy. Sale de contar: "
    f"de {conteos[2].sum()} aguaceros, {conteos[2, 2]} fueron seguidos por otro."
)

st.header("3. ¿Se alcanza un estado estable? (ítem 2)")
if analisis.converge:
    st.success("Sí, se alcanza: los tres tipos de día se comunican entre sí y la cadena es aperiódica.")
    en_resumen("el clima no está atado a un ciclo fijo, así que a largo plazo se estabiliza sin importar cómo empezó.")
else:
    st.warning("No se alcanza un estado estable con estos umbrales.")
    st.stop()

st.header("4. Distribución estacionaria frente a la realidad (ítem 3)")
comparacion = pd.DataFrame(
    {"Tipo de día": ESTADOS * 2, "Fuente": ["π del modelo"] * 3 + ["Frecuencia real"] * 3,
     "Proporción": np.concatenate([pi, frecuencia])}
)
columna_tabla, columna_barras = st.columns([1, 2], gap="large")
columna_tabla.dataframe(
    pd.DataFrame({"Tipo de día": ESTADOS, "π del modelo": pi, "Frecuencia real": frecuencia}).round(3),
    hide_index=True,
    width="stretch",
)
columna_barras.altair_chart(
    alt.Chart(comparacion)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X("Tipo de día:N", sort=ESTADOS, axis=alt.Axis(labelAngle=0), title=None),
        xOffset=alt.XOffset("Fuente:N", sort=["π del modelo", "Frecuencia real"]),
        y=alt.Y("Proporción:Q", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("Fuente:N", scale=alt.Scale(domain=["π del modelo", "Frecuencia real"], range=[AZUL, NARANJA]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=["Tipo de día:N", "Fuente:N", alt.Tooltip("Proporción:Q", format=".3f")],
    )
    .properties(height=260),
    width="stretch",
)
st.markdown(
    f"A largo plazo, Medellín tiene **{100 * pi[0]:.1f} %** de días secos, **{100 * pi[1]:.1f} %** de lluvia ligera "
    f"y **{100 * pi[2]:.1f} %** de lluvia fuerte. Coincide con lo que pasó de verdad en estos tres años."
)
en_resumen(f"a largo plazo, unos {round(100 * pi[0])} de cada 100 días son secos, y eso coincide con lo que pasó de verdad.")

st.header("5. ¿En cuántos días se olvida el clima de hoy? (ítem 4)")
if mezcla.t_mix is not None:
    st.markdown(
        f"Con ε = {epsilon:g}, el mixing time es **{mezcla.t_mix} días**: a partir de ahí, saber si hoy estuvo seco "
        "o lluvioso casi no cambia la probabilidad de cómo estará ese día."
    )
# Con ε = 0 la curva sigue después del mixing time y se ve que continúa bajando
distancias = mezcla.distancias if mezcla.t_mix is None else mixing_time(P, 0.0, max(10, 2 * mezcla.t_mix)).distancias
curva = pd.DataFrame({"Día t": range(len(distancias)), "d(t)": distancias})
st.altair_chart(
    alt.Chart(curva).mark_line(point=True, color=AZUL).encode(
        x=alt.X("Día t:Q", axis=alt.Axis(tickMinStep=1, format="d")),
        y=alt.Y("d(t):Q", title="Distancia a π (peor caso)"),
        tooltip=["Día t:Q", alt.Tooltip("d(t):Q", format=".4f")],
    )
    + alt.Chart(pd.DataFrame({"ε": [epsilon]})).mark_rule(strokeDash=[6, 4], color="#475569").encode(y="ε:Q"),
    width="stretch",
)
dias_memoria = "unos días" if mezcla.t_mix is None else f"{mezcla.t_mix} días"
en_resumen(f"después de {dias_memoria}, saber cómo estuvo hoy ya casi no ayuda a predecir el clima.")

st.header("6. El modelo frente a lo que pasó de verdad")
hoy = st.selectbox("Si hoy fue un día de…", ESTADOS, index=2)
origen = ESTADOS.index(hoy)
filas = []
for k in range(1, DIAS_COMPARACION + 1):
    modelo = np.linalg.matrix_power(P, k)[origen]  # Pᵏ predice el estado a k días
    real = frecuencia_a_k_pasos(datos["estado"].to_numpy(), origen, k, 3)
    filas += [{"k días después": k, "Fuente": "Modelo de Markov", "Probabilidad": modelo[2]},
              {"k días después": k, "Fuente": "Realidad", "Probabilidad": real[2]}]
validacion = pd.DataFrame(filas)
st.altair_chart(
    alt.Chart(validacion).mark_line(point=True).encode(
        x=alt.X("k días después:Q", axis=alt.Axis(tickMinStep=1, format="d")),
        y=alt.Y("Probabilidad:Q", title="Probabilidad de lluvia fuerte", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("Fuente:N", scale=alt.Scale(domain=["Modelo de Markov", "Realidad"], range=[AZUL, NARANJA]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=["k días después:Q", "Fuente:N", alt.Tooltip("Probabilidad:Q", format=".3f")],
    )
    + alt.Chart(pd.DataFrame({"π": [pi[2]]})).mark_rule(strokeDash=[6, 4], color="#475569").encode(y="π:Q"),
    width="stretch",
)
real_5 = frecuencia_a_k_pasos(datos["estado"].to_numpy(), origen, 5, 3)[2]
modelo_5 = np.linalg.matrix_power(P, 5)[origen][2]
st.markdown(
    f"Al día siguiente el modelo coincide exacto con la realidad, porque P se estimó justo con esos pares de días. "
    f"Más adelante se separan: 5 días después de un día de {hoy.lower()}, el modelo predice **{100 * modelo_5:.1f} %** de "
    f"lluvia fuerte y en la realidad fue **{100 * real_5:.1f} %**. La línea punteada es π."
)
diferencia = validacion.pivot(index="k días después", columns="Fuente", values="Probabilidad").iloc[1:]
diferencia = float((diferencia["Realidad"] - diferencia["Modelo de Markov"]).mean())
if diferencia > 0.02:
    lectura = "después de un aguacero sigue lloviendo más de lo que predice el modelo: las temporadas de lluvia duran más de lo que la cadena cree."
elif diferencia < -0.02:
    lectura = "después de un día seco llueve menos de lo que predice el modelo: las temporadas secas duran más de lo que la cadena cree."
else:
    lectura = "desde este tipo de día el modelo acierta bien."
en_resumen(lectura)
st.info(
    "**Conclusión:** la cadena de Markov solo mira el día anterior, así que olvida rápido. "
    "El clima real tiene temporadas de lluvia y temporadas secas que duran semanas, y por eso recuerda más "
    "de lo que supone el modelo. El mixing time es un buen límite inferior: el clima de hoy se olvida en "
    f"al menos {mezcla.t_mix} días, y en la práctica tarda un poco más."
)
