from streamlit.testing.v1 import AppTest


def abrir(ejemplo=None):
    # El primer arranque en frío de la máquina puede pasar de 30 s
    app = AppTest.from_file("../simulador/app.py", default_timeout=120).run()
    if ejemplo:
        app.selectbox(key="ejemplo").select(ejemplo).run()
    assert not app.exception
    return app


def textos(elementos):
    return " ".join(e.value for e in elementos)


def metricas(app):
    return {m.label: m.value for m in app.metric}


def test_resumen_de_cadena_regular():
    app = abrir("Regular (2 estados)")
    resumen = metricas(app)
    assert resumen["¿Estado estable?"] == "Sí"
    assert resumen["Mixing time"] == "2"
    assert resumen["|λ₂|"] == "0.4000"
    assert resumen["Estado más probable"] == "E1"
    assert "alcanza" in textos(app.success)


def test_resumen_de_cadena_periodica_explica_por_que_no_converge():
    app = abrir("Periódica (2 estados)")
    resumen = metricas(app)
    assert resumen["¿Estado estable?"] == "No"
    assert resumen["Período"] == "2"
    assert "Mixing time" not in resumen
    assert "período 2" in textos(app.warning)


def test_resumen_de_dos_clases_cerradas():
    app = abrir("Dos estados absorbentes")
    resumen = metricas(app)
    assert resumen["¿Estado estable?"] == "No"
    assert resumen["Clases cerradas"] == "2"
    assert "2 clases cerradas" in textos(app.warning)


def test_matriz_personalizada_arranca_con_fracciones_validas():
    app = abrir("Personalizada")
    assert metricas(app)["Mixing time"] == "1"


def test_la_matriz_de_partida_se_elige_en_la_barra_lateral():
    app = abrir()
    assert any(s.key == "ejemplo" for s in app.sidebar.selectbox)


def test_animacion_muestra_la_distancia_del_paso_elegido():
    app = abrir("Regular (2 estados)")
    app.slider(key="paso_animacion").set_value(1).run()
    assert "En t = 1 la distancia a π es 0.0667" in textos(app.caption)


def test_cada_seccion_tiene_su_explicacion():
    app = abrir("Regular (2 estados)")
    assert sum("¿Qué significa?" in e.label for e in app.expander) >= 5


def test_pie_de_pagina_con_los_integrantes():
    app = abrir()
    assert "Juan José Ospina" in textos(app.caption)
