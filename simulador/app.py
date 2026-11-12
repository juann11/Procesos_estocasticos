"""Menú de la aplicación: el simulador, el caso real y el experimento con cartas."""
import streamlit as st

st.navigation(
    [
        st.Page("pagina_simulador.py", title="Simulador", icon=":material/calculate:", default=True),
        st.Page("pagina_clima.py", title="Caso real: clima de Medellín", icon=":material/rainy:"),
        st.Page("pagina_cartas.py", title="Experimento: barajar cartas", icon=":material/casino:"),
    ]
).run()
