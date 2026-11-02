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


def test_cadena_regular_muestra_estado_estable_y_mixing_time():
    app = abrir("Regular (2 estados)")
    assert "alcanza" in textos(app.success)
    assert app.metric[0].value == "2"
    assert len(app.dataframe) >= 1


def test_cadena_periodica_explica_por_que_no_converge():
    app = abrir("Periódica (2 estados)")
    assert "período 2" in textos(app.warning)
    assert not app.metric


def test_dos_clases_cerradas_explica_por_que_no_converge():
    app = abrir("Dos estados absorbentes")
    assert "2 clases cerradas" in textos(app.warning)
    assert not app.metric
