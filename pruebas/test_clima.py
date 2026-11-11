from streamlit.testing.v1 import AppTest


def abrir():
    # El primer arranque en frío de la máquina puede pasar de 30 s
    app = AppTest.from_file("../simulador/pagina_clima.py", default_timeout=120).run()
    assert not app.exception
    return app


def textos(elementos):
    return " ".join(e.value for e in elementos)


def metricas(app):
    return {m.label: m.value for m in app.metric}


def test_resumen_con_los_datos_reales_de_medellin():
    resumen = metricas(abrir())
    assert resumen["Días analizados"] == "1096"
    assert resumen["Mixing time"] == "2 días"
    assert resumen["Días secos a largo plazo"] == "29.4 %"


def test_la_cadena_del_clima_alcanza_estado_estable():
    assert "alcanza" in textos(abrir().success)


def test_umbral_sin_datos_explica_el_problema():
    app = abrir()
    app.number_input(key="umbral_fuerte").set_value(100.0).run()
    assert "sin datos" in textos(app.error)


def test_explica_como_se_conecta_con_el_taller():
    app = abrir()
    assert any("taller" in e.label for e in app.expander)


def test_cada_paso_tiene_una_explicacion_sencilla():
    app = abrir()
    sencillas = [i.value for i in app.info if i.value.startswith("**En palabras sencillas:**")]
    assert len(sencillas) == 6
