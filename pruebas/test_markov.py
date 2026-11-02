import numpy as np
import pytest

from markov import (
    analizar_cadena,
    clases_comunicantes,
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

REGULAR = [[0.9, 0.1], [0.5, 0.5]]


# Ítem 1: validación de la entrada


def test_acepta_matriz_estocastica():
    assert validar_matriz(REGULAR) == []


def test_rechaza_valores_negativos():
    errores = validar_matriz([[1.5, -0.5], [0.5, 0.5]])
    assert any("negativ" in e for e in errores)


def test_rechaza_fila_que_no_suma_uno_e_indica_cual():
    errores = validar_matriz([[0.9, 0.1], [0.5, 0.4]])
    assert any("Fila 2" in e for e in errores)


def test_rechaza_valores_vacios():
    errores = validar_matriz([[0.5, float("nan")], [0.5, 0.5]])
    assert any("vací" in e for e in errores)


def test_rechaza_matriz_no_cuadrada():
    assert validar_matriz([[0.5, 0.5]]) != []


def test_tolera_redondeo_en_la_suma():
    assert validar_matriz([[0.1 + 0.2, 0.7], [1 / 3, 2 / 3]]) == []


# Ítem 2: clases comunicantes, período y convergencia


def test_agrupa_clases_comunicantes():
    P = [[0.5, 0.5, 0], [0.5, 0.5, 0], [0.2, 0, 0.8]]
    clases = sorted(sorted(c) for c in clases_comunicantes(np.array(P)))
    assert clases == [[0, 1], [2]]


def test_cadena_regular_converge():
    resultado = analizar_cadena(REGULAR)
    assert resultado.converge
    assert resultado.periodo == 1


def test_cadena_periodica_no_converge():
    resultado = analizar_cadena([[0, 1], [1, 0]])
    assert not resultado.converge
    assert resultado.periodo == 2


def test_periodo_tres_en_ciclo():
    resultado = analizar_cadena([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    assert not resultado.converge
    assert resultado.periodo == 3


def test_ciclos_de_longitud_2_y_3_dan_cadena_aperiodica():
    resultado = analizar_cadena([[0, 1, 0], [0.5, 0, 0.5], [1, 0, 0]])
    assert resultado.converge
    assert resultado.periodo == 1


def test_camino_bipartito_tiene_periodo_dos():
    P = [[0, 1, 0, 0], [0.5, 0, 0.5, 0], [0, 0.5, 0, 0.5], [0, 0, 1, 0]]
    resultado = analizar_cadena(P)
    assert not resultado.converge
    assert resultado.periodo == 2


def test_cadena_con_dos_estados_absorbentes_no_converge():
    P = [[1, 0, 0], [0.3, 0.4, 0.3], [0, 0, 1]]
    resultado = analizar_cadena(P)
    assert not resultado.converge
    assert sorted(sorted(c) for c in resultado.clases_cerradas) == [[0], [2]]


def test_estados_transitorios_no_impiden_la_convergencia():
    P = [[0.5, 0.5, 0], [0, 0.5, 0.5], [0, 0, 1]]
    resultado = analizar_cadena(P)
    assert resultado.converge
    assert resultado.clases_cerradas == [[2]]


def test_una_salida_diminuta_impide_que_la_clase_sea_cerrada():
    resultado = analizar_cadena([[1, 1e-10], [0, 1]])
    assert resultado.clases_cerradas == [[1]]


def test_autolazo_vuelve_aperiodica_la_clase():
    resultado = analizar_cadena([[0, 1], [0.5, 0.5]])
    assert resultado.converge
    assert resultado.periodo == 1


# Ítem 3: distribución de estado estable


def test_distribucion_estacionaria_regular():
    pi = distribucion_estacionaria(REGULAR)
    assert pi == pytest.approx([5 / 6, 1 / 6])


def test_distribucion_estacionaria_concentrada_en_absorbente():
    P = [[0.5, 0.5, 0], [0, 0.5, 0.5], [0, 0, 1]]
    assert distribucion_estacionaria(P) == pytest.approx([0, 0, 1], abs=1e-9)


def test_distribucion_estacionaria_es_punto_fijo():
    P = np.array([[0.2, 0.5, 0.3], [0.4, 0.1, 0.5], [0.3, 0.3, 0.4]])
    pi = distribucion_estacionaria(P)
    assert pi @ P == pytest.approx(pi)
    assert pi.sum() == pytest.approx(1)


# Ítem 4: mixing time


def test_mixing_time_del_ejemplo_a_mano():
    resultado = mixing_time(REGULAR)
    assert resultado.t_mix == 2
    assert resultado.distancias == pytest.approx([5 / 6, 1 / 3, 2 / 15])


def test_mixing_time_con_epsilon_menor_tarda_mas():
    assert mixing_time(REGULAR, epsilon=0.01).t_mix == 5


def test_mixing_time_es_cero_si_ya_arranca_mezclada():
    assert mixing_time([[0.5, 0.5], [0.5, 0.5]], epsilon=0.5).t_mix == 0


def test_mixing_time_informa_si_no_alcanza_el_limite():
    lenta = [[1 - 1e-7, 1e-7], [1e-7, 1 - 1e-7]]
    resultado = mixing_time(lenta, max_pasos=50)
    assert resultado.t_mix is None
    assert len(resultado.distancias) == 51


# Ítem 5: simulación Monte Carlo


def test_simulacion_se_acerca_a_la_estacionaria():
    resultado = simular(REGULAR, estado_inicial=1, caminantes=100_000, pasos=30, semilla=1)
    assert resultado[-1] == pytest.approx([5 / 6, 1 / 6], abs=0.01)


def test_simulacion_arranca_en_el_estado_inicial():
    resultado = simular(REGULAR, estado_inicial=1, caminantes=10, pasos=3, semilla=1)
    assert resultado[0] == pytest.approx([0, 1])
    assert resultado.shape == (4, 2)


def test_simulacion_nunca_visita_estados_con_probabilidad_cero():
    P = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    resultado = simular(P, estado_inicial=0, caminantes=1000, pasos=1, semilla=1)
    assert resultado[1] == pytest.approx([0, 1, 0])


def test_simulacion_con_la_misma_semilla_es_reproducible():
    a = simular(REGULAR, 0, 100, 10, semilla=7)
    b = simular(REGULAR, 0, 100, 10, semilla=7)
    assert np.array_equal(a, b)


def test_distancia_tv_entre_distribuciones_opuestas_es_uno():
    assert distancia_tv([1, 0], [0, 1]) == pytest.approx(1)


def test_evolucion_exacta_coincide_con_potencias_de_la_matriz():
    evolucion = evolucion_exacta(REGULAR, estado_inicial=1, pasos=3)
    assert evolucion[0] == pytest.approx([0, 1])
    assert evolucion[3] == pytest.approx(np.linalg.matrix_power(np.array(REGULAR), 3)[1])


# Lectura de la tabla: decimales, coma decimal y fracciones


def test_lee_decimales_comas_y_fracciones():
    P, errores = leer_matriz([["0.25", "3/4"], ["0,5", " 1/2 "]])
    assert errores == []
    assert P.tolist() == [[0.25, 0.75], [0.5, 0.5]]


def test_tres_tercios_en_fraccion_forman_una_fila_valida():
    P, errores = leer_matriz([["1/3", "1/3", "1/3"]] * 3)
    assert errores == []
    assert validar_matriz(P) == []


def test_lectura_indica_la_casilla_que_no_es_un_numero():
    _, errores = leer_matriz([["0.5", "hola"], ["0.5", "0.5"]])
    assert errores == ["Fila 1, columna 2: «hola» no es un número."]


def test_lectura_rechaza_division_por_cero_y_numeros_gigantes():
    _, errores = leer_matriz([["1/0", "1e999"], ["0.5", "0.5"]])
    assert len(errores) == 2


def test_lectura_indica_las_casillas_vacias():
    _, errores = leer_matriz([["", None], ["0.5", float("nan")]])
    assert errores == [
        "Fila 1, columna 1 está vacía.",
        "Fila 1, columna 2 está vacía.",
        "Fila 2, columna 2 está vacía.",
    ]


# Velocidad de convergencia y grafo


def test_segundo_valor_propio_coincide_con_el_ejemplo_a_mano():
    assert segundo_valor_propio(REGULAR) == pytest.approx(0.4)


def test_segundo_valor_propio_es_cero_si_mezcla_en_un_paso():
    assert segundo_valor_propio([[0.5, 0.5], [0.5, 0.5]]) == pytest.approx(0, abs=1e-12)


def test_grafo_dibuja_solo_las_transiciones_posibles():
    P = [[0.5, 0.5], [0, 1]]
    dot = grafo_dot(P, [[1]])
    assert 'E1 -> E2 [label="0.5"]' in dot
    assert "E2 -> E1" not in dot


def test_grafo_marca_con_doble_circulo_las_clases_cerradas():
    dot = grafo_dot([[0.5, 0.5], [0, 1]], [[1]])
    assert "E2 [peripheries=2" in dot
    assert "E1 [peripheries=1" in dot
