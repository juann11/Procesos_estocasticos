import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from markov import (
    analizar_cadena,
    barajadas_equivalentes,
    distancia_barajado,
    distribucion_subidas,
    eulerianos,
    leer_experimento,
    matriz_riffle,
    mixing_time,
    riffle,
    secuencias_ascendentes,
    simular_experimento,
    subidas,
    validar_matriz,
)


# Secuencias ascendentes: cuántos tramos crecientes de valores consecutivos tiene el mazo


def test_mazo_ordenado_tiene_una_secuencia_ascendente():
    assert subidas([1, 2, 3, 4, 5]) == 1


def test_una_barajada_riffle_deja_dos_secuencias_ascendentes():
    # 1, 2 vienen de un montón y 3, 4, 5 del otro
    assert subidas([3, 1, 4, 2, 5]) == 2


def test_mazo_invertido_tiene_tantas_secuencias_como_cartas():
    assert subidas([4, 3, 2, 1]) == 4


def test_numeros_eulerianos_cuentan_permutaciones_por_secuencias():
    assert eulerianos(4) == [1, 11, 11, 1]
    assert sum(eulerianos(6)) == 720


# El barajado como cadena de Markov


def test_matriz_riffle_es_estocastica():
    P, _ = matriz_riffle(4)
    assert P.shape == (24, 24)
    assert validar_matriz(P) == []


def test_desde_el_orden_inicial_queda_igual_con_probabilidad_n_mas_1_sobre_2_a_la_n():
    P, ordenes = matriz_riffle(3)
    inicio = ordenes.index((1, 2, 3))
    assert P[inicio, inicio] == pytest.approx(4 / 8)


def test_el_barajado_converge_a_todos_los_ordenes_por_igual():
    P, _ = matriz_riffle(4)
    assert analizar_cadena(P).converge


def test_la_formula_exacta_coincide_con_la_matriz_del_simulador():
    P, _ = matriz_riffle(4)
    desde_la_matriz = mixing_time(P, 0.0, 6).distancias
    for k in range(1, 7):
        assert distancia_barajado(4, k) == pytest.approx(desde_la_matriz[k], abs=1e-9)


def test_tabla_de_bayer_y_diaconis_para_52_cartas():
    assert distancia_barajado(52, 6) == pytest.approx(0.614, abs=0.001)
    assert distancia_barajado(52, 7) == pytest.approx(0.334, abs=0.001)
    assert distancia_barajado(52, 8) == pytest.approx(0.167, abs=0.001)


def test_distribucion_de_secuencias_suma_uno_y_tiende_a_la_uniforme():
    teorica = distribucion_subidas(6, 3)
    assert teorica.sum() == pytest.approx(1)
    uniforme = np.array(eulerianos(6)) / 720
    assert distribucion_subidas(6, 40) == pytest.approx(uniforme, abs=1e-9)


# Datos del experimento real


def test_lee_el_experimento_por_lineas():
    ensayos, errores = leer_experimento("1: 3 1 4 2 5\n2: 2 5 1 3 4\n\n1: 1 2 3 4 5")
    assert errores == []
    assert ensayos == [(1, [3, 1, 4, 2, 5]), (2, [2, 5, 1, 3, 4]), (1, [1, 2, 3, 4, 5])]


def test_experimento_con_carta_repetida_indica_la_linea():
    _, errores = leer_experimento("1: 3 1 4 2 5\n1: 3 3 4 2 5")
    assert errores == ["Línea 2: debe tener cada número del 1 al 5 una sola vez."]


def test_experimento_mal_escrito_indica_la_linea():
    _, errores = leer_experimento("una barajada: 3 1 4")
    assert errores == ["Línea 1: escribe «barajadas: orden», por ejemplo «2: 3 1 5 2 4»."]


def test_barajadas_equivalentes_reconoce_datos_del_modelo():
    teorica = distribucion_subidas(10, 2)
    assert barajadas_equivalentes(teorica, 10) == 2


# Riffle interactivo y datos de prueba


def test_colorea_cada_carta_con_su_secuencia_ascendente():
    # 1, 2 forman la secuencia 1 y 3, 4, 5 la secuencia 2
    assert secuencias_ascendentes([3, 1, 4, 2, 5]) == [2, 1, 2, 1, 2]
    assert secuencias_ascendentes([1, 2, 3]) == [1, 1, 1]


def test_riffle_entrelaza_dos_montones_sin_desordenarlos():
    resultado, corte = riffle(list(range(1, 11)), np.random.default_rng(4))
    assert sorted(resultado) == list(range(1, 11))
    assert subidas(resultado) <= 2
    de_arriba = [c for c in resultado if c <= corte]
    assert de_arriba == sorted(de_arriba)


def test_datos_simulados_se_leen_como_un_experimento():
    texto = simular_experimento(10, [1, 2], intentos=5, semilla=1)
    ensayos, errores = leer_experimento(texto)
    assert errores == []
    assert len(ensayos) == 10
    assert texto == simular_experimento(10, [1, 2], intentos=5, semilla=1)


# Página del experimento


def abrir():
    app = AppTest.from_file("../simulador/pagina_cartas.py", default_timeout=120).run()
    assert not app.exception
    return app


def textos(elementos):
    return " ".join(e.value for e in elementos)


def test_pagina_muestra_las_barajadas_necesarias_para_52_cartas():
    resumen = {m.label: m.value for m in abrir().metric}
    assert resumen["Barajadas para mezclar 52 cartas"] == "8"


def test_boton_de_barajar_hace_un_riffle():
    app = abrir()
    app.button(key="barajar_demo").click().run()
    assert app.session_state["demo_barajadas"] == 1


def test_registrar_un_intento_tocando_las_cartas():
    app = abrir()
    app.number_input(key="cartas_experimento").set_value(4).run()
    for carta in (3, 1, 4, 2):
        app.button(key=f"carta_{carta}").click().run()
    app.button(key="guardar_intento").click().run()
    assert app.session_state["intentos"] == [(1, [3, 1, 4, 2])]


def test_pegar_resultados_compara_con_la_teoria():
    app = abrir()
    app.text_area(key="pegar").set_value("1: 3 1 4 2 5\n1: 1 4 2 5 3\n2: 2 5 1 3 4")
    app.button(key="agregar_pegados").click().run()
    assert "quedó como con" in textos(app.markdown)


def test_pegar_resultados_con_errores_los_explica():
    app = abrir()
    app.text_area(key="pegar").set_value("1: 3 3 4 2 5")
    app.button(key="agregar_pegados").click().run()
    assert "una sola vez" in textos(app.error)


def test_datos_simulados_dejan_probar_al_instante():
    app = abrir()
    app.button(key="datos_simulados").click().run()
    assert "quedó como con" in textos(app.markdown)
    assert "simulad" in textos(app.warning)
