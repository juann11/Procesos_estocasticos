"""Menú de la aplicación: el simulador y el caso real."""
import streamlit as st

st.navigation(
    [
        st.Page("pagina_simulador.py", title="Simulador", icon=":material/calculate:", default=True),
        st.Page("pagina_clima.py", title="Caso real: clima de Medellín", icon=":material/rainy:"),
    ]
).run()
