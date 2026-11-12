"""Experimento: ¿cuántas veces hay que barajar un mazo para que quede bien mezclado?"""
from collections import Counter, defaultdict
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
    riffle,
    secuencias_ascendentes,
    simular_experimento,
    subidas,
)

AZUL = "#2a78d6"
NARANJA = "#eb6834"
GRIS = "#475569"
EPSILON = 0.25
MAX_BARAJADAS = 12
CARTAS_DEMO = 10
# Fondos claros con texto oscuro: cada secuencia ascendente tiene su color y además su número
COLORES_SECUENCIA = ["#DBEAFE", "#FDE2CF", "#D1FAE5", "#FEF3C7", "#EDE9FE", "#FCE7F3", "#E0F2FE", "#ECFCCB"]
BORDES_SECUENCIA = ["#2a78d6", "#C2410C", "#047857", "#B45309", "#6D28D9", "#BE185D", "#0369A1", "#4D7C0F"]


def barajadas(k: int) -> str:
    return f"{k} barajada" if k == 1 else f"{k} barajadas"


def en_resumen(texto: str):
    st.info(f"**En resumen:** {texto}", icon=":material/lightbulb:")


def cartas_html(orden, con_secuencias: bool = True) -> str:
    """Dibuja el mazo como fila de cartas; con secuencias, cada carta lleva el color y número de su secuencia."""
    grupos = secuencias_ascendentes(orden) if con_secuencias else [1] * len(orden)
    cartas = []
    for carta, grupo in zip(orden, grupos):
        fondo = COLORES_SECUENCIA[(grupo - 1) % len(COLORES_SECUENCIA)] if con_secuencias else "#FFFFFF"
        borde = BORDES_SECUENCIA[(grupo - 1) % len(BORDES_SECUENCIA)] if con_secuencias else "#94A3B8"
        etiqueta = f"<div style='font-size:11px;color:#334155'>S{grupo}</div>" if con_secuencias else ""
        cartas.append(
            f"<div style='width:46px;height:64px;border:2px solid {borde};border-radius:8px;background:{fondo};"
            f"display:flex;flex-direction:column;align-items:center;justify-content:center;"
            f"font-weight:600;font-size:20px;color:#0F172A'>{carta}{etiqueta}</div>"
        )
    return f"<div style='display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 12px'>{''.join(cartas)}</div>"


st.set_page_config(page_title="Experimento: barajar cartas", layout="wide")
st.title("Experimento: ¿cuántas veces hay que barajar?")
st.caption(
    "Barajar un mazo es una cadena de Markov: cada barajada cambia el orden de las cartas al azar. "
    "El mixing time responde cuántas barajadas hacen falta para que el mazo quede bien mezclado."
)

with st.expander("¿Cómo se conecta con el taller?"):
    st.markdown(
        "Cada **estado** es un orden posible del mazo y cada **paso** es una barajada tipo *riffle*: se corta el "
        "mazo en dos montones y se entrelazan. Usamos el modelo de Gilbert, Shannon y Reeds, que describe ese riffle.\n\n"
        "1. **Matriz estocástica:** para un mazo pequeño se construye completa, con un estado por cada orden.\n"
        "2. **¿Estado estable?** Se aplica el mismo criterio del simulador.\n"
        "3. **Distribución estacionaria:** todos los órdenes igual de probables, es decir, un mazo bien mezclado.\n"
        "4. **Mixing time:** cuántas barajadas hacen falta.\n"
        "5. **Experimento propio:** barajamos un mazo real y comparamos nuestras barajadas con el modelo."
    )

# 1. Riffle interactivo
st.header("1. Así funciona un riffle")
st.markdown(
    "Se corta el mazo en dos montones y se entrelazan, dejando caer las cartas de uno y otro. "
    "Dale **Barajar** y mira qué le pasa al mazo."
)
estado = st.session_state
estado.setdefault("demo_mazo", list(range(1, CARTAS_DEMO + 1)))
estado.setdefault("demo_barajadas", 0)
estado.setdefault("demo_ultimo", None)


def barajar_demo():
    antes = estado.demo_mazo
    despues, corte = riffle(antes, np.random.default_rng())
    estado.demo_ultimo = (antes, corte)
    estado.demo_mazo = despues
    estado.demo_barajadas += 1


def reiniciar_demo():
    estado.demo_mazo = list(range(1, CARTAS_DEMO + 1))
    estado.demo_barajadas = 0
    estado.demo_ultimo = None


botones = st.container(horizontal=True)
botones.button("Barajar", key="barajar_demo", on_click=barajar_demo, type="primary", width="content",
                  icon=":material/shuffle:")
botones.button("Ordenar de nuevo", key="reiniciar_demo", on_click=reiniciar_demo, width="content",
                  icon=":material/restart_alt:")

if estado.demo_ultimo:
    antes, corte = estado.demo_ultimo
    montones = st.columns(2)
    montones[0].caption(f"Montón de arriba ({corte} cartas)")
    montones[0].markdown(cartas_html(antes[:corte], con_secuencias=False), unsafe_allow_html=True)
    montones[1].caption(f"Montón de abajo ({len(antes) - corte} cartas)")
    montones[1].markdown(cartas_html(antes[corte:], con_secuencias=False), unsafe_allow_html=True)

st.caption("El mazo ahora, de arriba abajo. Cada color (S1, S2…) es una secuencia ascendente:")
st.markdown(cartas_html(estado.demo_mazo), unsafe_allow_html=True)
contador = st.columns(3)
contador[0].metric("Barajadas hechas", estado.demo_barajadas, border=True)
contador[1].metric("Secuencias ascendentes", subidas(estado.demo_mazo), border=True)
contador[2].metric(
    "Promedio ya mezclado", f"{(CARTAS_DEMO + 1) / 2:g}", border=True,
    help="Un mazo de n cartas perfectamente mezclado tiene en promedio (n + 1) / 2 secuencias ascendentes.",
)
en_resumen(
    "una secuencia ascendente es un grupo de cartas consecutivas (1, 2, 3…) que siguen en orden de arriba abajo. "
    "Cada riffle como mucho duplica las secuencias: 1 → 2 → 4 → 8… Por eso un solo riffle nunca mezcla bien "
    "y hacen falta varios."
)

# 2. Mazo pequeño: la matriz completa con el mismo simulador
st.header("2. Un mazo pequeño como cadena de Markov")
n_pequeno = st.number_input("Cartas del mazo pequeño", min_value=3, max_value=5, value=4, key="mazo_pequeno")
P, ordenes = matriz_riffle(n_pequeno)
analisis = analizar_cadena(P)
mezcla = mixing_time(P, EPSILON)
pequeno = st.columns(4)
pequeno[0].metric("Órdenes posibles (estados)", len(ordenes), border=True)
pequeno[1].metric("¿Estado estable?", "Sí" if analisis.converge else "No", border=True)
pequeno[2].metric("Probabilidad de cada orden (π)", f"1/{len(ordenes)}", border=True)
pequeno[3].metric("Barajadas para mezclar", mezcla.t_mix, help=f"Mixing time con ε = {EPSILON:g}", border=True)
st.markdown(
    f"La matriz tiene {len(ordenes)} × {len(ordenes)} entradas: una fila y una columna por cada orden del mazo. "
    f"Desde cualquier orden, un riffle deja el mazo igual con probabilidad {n_pequeno + 1}/{2 ** n_pequeno} y lleva "
    f"a cada orden con dos secuencias ascendentes con probabilidad 1/{2 ** n_pequeno}. El simulador encuentra una sola "
    "clase cerrada y aperiódica, y π reparte la probabilidad por igual entre todos los órdenes."
)
en_resumen(
    f"con {n_pequeno} cartas basta con {barajadas(mezcla.t_mix)} para que cualquier orden sea casi igual de probable."
)

# 3. Mazo completo: fórmula exacta de Bayer y Diaconis
st.header("3. Un mazo de 52 cartas")
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
    "un mazo bien mezclado de 52 cartas tiene unas 26 secuencias ascendentes, y como cada riffle como mucho las "
    "duplica, con 4 barajadas (máximo 16) es imposible llegar: el mazo sigue casi en orden. Entre la quinta y la "
    f"octava se mezcla de golpe y con {barajadas(t_mix_52)} baja de ε = {EPSILON:g}. De ese salto sale el famoso "
    "«7 barajadas»."
)

# 4. Experimento con un mazo real
st.header("4. Nuestro experimento: ¿barajamos como el modelo?")
st.markdown(
    "Tomen cartas numeradas en orden (por ejemplo, del as al 10), háganles una cantidad de riffles y registren cómo "
    "quedó el mazo. Repitan varias veces: **entre más intentos, más confiable el resultado.**"
)
estado.setdefault("intentos", [])
estado.setdefault("registro", [])
estado.setdefault("hay_simulados", False)

configuracion = st.columns(2)
n_cartas = configuracion[0].number_input(
    "Cartas del mazo", min_value=4, max_value=13, value=10, key="cartas_experimento",
    help="Usen cartas numeradas del 1 al n, ordenadas de arriba abajo antes de barajar.",
)
k_actual = configuracion[1].number_input("Barajadas que hicieron", min_value=1, max_value=10, value=1,
                                         key="barajadas_intento")
if any(carta > n_cartas for carta in estado.registro):
    estado.registro = []


def tocar_carta(carta: int):
    estado.registro.append(carta)


def guardar_intento():
    estado.intentos.append((k_actual, list(estado.registro)))
    estado.registro = []


def agregar_pegados():
    ensayos, errores = leer_experimento(estado.pegar)
    estado.errores_pegados = errores
    if not errores:
        estado.intentos.extend(ensayos)


def agregar_simulados():
    texto = simular_experimento(10, [1, 2, 3], intentos=15)
    estado.intentos.extend(leer_experimento(texto)[0])
    estado.hay_simulados = True


def borrar_intentos():
    estado.intentos = []
    estado.registro = []
    estado.hay_simulados = False


registrar, pegar, probar = st.tabs(["Registrar con clics", "Pegar resultados", "Probar sin barajar"])
with registrar:
    st.markdown(
        f"Después de **{barajadas(k_actual)}**, toquen las cartas en el orden en que quedaron, **de arriba abajo**."
    )
    if estado.registro:
        st.markdown(cartas_html(estado.registro, con_secuencias=False), unsafe_allow_html=True)
    else:
        st.caption("Todavía no han tocado ninguna carta.")
    pendientes = [c for c in range(1, n_cartas + 1) if c not in estado.registro]
    if pendientes:
        teclas = st.columns(n_cartas)
        for posicion, carta in enumerate(pendientes):
            teclas[posicion].button(str(carta), key=f"carta_{carta}", on_click=tocar_carta, args=(carta,),
                                    width="stretch")
    acciones = st.container(horizontal=True)
    acciones.button("Guardar intento", key="guardar_intento", on_click=guardar_intento, type="primary",
                       disabled=len(estado.registro) != n_cartas, width="content", icon=":material/check:")
    acciones.button("Deshacer", key="deshacer", on_click=lambda: estado.registro.pop() if estado.registro else None,
                       disabled=not estado.registro, width="content", icon=":material/undo:")
with pegar:
    st.markdown("Si ya tienen los resultados escritos, péguenlos con una línea por intento: `barajadas: orden`.")
    st.text_area("Resultados", key="pegar", height=140, placeholder="1: 6 1 7 2 8 3 9 4 10 5\n2: 3 8 1 6 9 4 2 10 7 5")
    st.button("Agregar estos resultados", key="agregar_pegados", on_click=agregar_pegados, icon=":material/add:")
    for error in estado.get("errores_pegados", []):
        st.error(error)
with probar:
    st.markdown(
        "¿No tienen cartas a la mano? Generen 45 intentos de prueba con el modelo (15 de 1, 2 y 3 barajadas) "
        "para ver cómo funciona el análisis. **No son barajadas reales.**"
    )
    st.button("Generar datos simulados", key="datos_simulados", on_click=agregar_simulados, icon=":material/science:")

if not estado.intentos:
    st.info("Cuando registren sus intentos, aquí aparece la comparación con el modelo.", icon=":material/style:")
    st.stop()

if estado.hay_simulados:
    st.warning("Estos resultados incluyen datos simulados por computador, no barajadas reales.", icon=":material/science:")
n = Counter(len(orden) for _, orden in estado.intentos).most_common(1)[0][0]
ignorados = sum(len(orden) != n for _, orden in estado.intentos)
if ignorados:
    st.warning(f"Se ignoran {ignorados} intentos que no tienen {n} cartas.")
por_barajadas = defaultdict(list)
for k, orden in estado.intentos:
    if len(orden) == n:
        por_barajadas[k].append(subidas(orden))

st.subheader("Resultados")
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
for fila in filas:
    st.markdown(
        f"- Con **{barajadas(fila['Barajadas reales'])}**, el mazo quedó como con "
        f"**{barajadas(fila['Equivalen a barajadas del modelo'])}** del modelo ({fila['Intentos']} intentos)."
    )
st.dataframe(pd.DataFrame(filas).round(3), hide_index=True, width="stretch")

k_elegido = st.selectbox("Ver el detalle de", sorted(por_barajadas), format_func=barajadas)
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
    f"Con pocas barajadas el modelo predice pocas secuencias ascendentes; en un mazo bien mezclado de {n} cartas el "
    f"promedio es {float(np.dot(range(1, n + 1), np.array(eulerianos(n)) / factorial(n))):.1f}."
)
en_resumen(
    "si sus barajadas «equivalen» a menos barajadas del modelo, es porque al entrelazar las cartas caen en grupos y no "
    "una por una, así que el mazo se mezcla más despacio. Con pocos intentos el resultado varía bastante."
)

guardar = st.container(horizontal=True)
guardar.download_button(
    "Descargar intentos",
    "\n".join(f"{k}: {' '.join(map(str, orden))}" for k, orden in estado.intentos),
    file_name="intentos_barajadas.txt",
    icon=":material/download:",
    width="content",
)
guardar.button("Borrar todos", key="borrar_intentos", on_click=borrar_intentos, width="content",
                  icon=":material/delete:")
st.caption("Descarguen sus intentos antes de cerrar la página; luego pueden pegarlos en la pestaña «Pegar resultados».")
