"""Lógica de cadenas de Markov: validación, convergencia, estado estable y mixing time."""
from collections import deque
from dataclasses import dataclass
import re
from fractions import Fraction
from itertools import permutations
from math import comb, factorial, gcd

import numpy as np

TOLERANCIA_SUMA = 1e-9
TOLERANCIA_REDONDEO = 1e-12


@dataclass
class Analisis:
    clases: list[list[int]]
    clases_cerradas: list[list[int]]
    periodo: int | None  # solo se define cuando hay una única clase cerrada
    converge: bool


@dataclass
class Mezcla:
    t_mix: int | None  # None si no se alcanzó epsilon dentro de max_pasos
    distancias: list[float]


def leer_matriz(celdas) -> tuple[np.ndarray, list[str]]:
    """Convierte el texto de la tabla a números; acepta 0.25, 0,25 y 1/3."""
    errores = []
    P = np.full((len(celdas), len(celdas[0])), np.nan)
    for i, fila in enumerate(celdas):
        for j, celda in enumerate(fila):
            texto = celda.strip() if isinstance(celda, str) else ""
            if not texto:
                errores.append(f"Fila {i + 1}, columna {j + 1} está vacía.")
                continue
            try:
                P[i, j] = float(Fraction(texto.replace(",", ".")))
            except (ValueError, ZeroDivisionError, OverflowError):
                errores.append(f"Fila {i + 1}, columna {j + 1}: «{texto}» no es un número.")
    return P, errores


def validar_matriz(P) -> list[str]:
    """Devuelve los errores encontrados; la lista vacía significa que P es estocástica."""
    try:
        P = np.array(P, dtype=float)
    except (TypeError, ValueError):
        return ["La matriz tiene valores que no son números o filas de distinto tamaño."]
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        return ["La matriz debe ser cuadrada."]
    if np.isnan(P).any():
        return ["Hay casillas vacías."]

    errores = []
    if (P < 0).any():
        errores.append("Hay valores negativos.")
    for i, suma in enumerate(P.sum(axis=1), 1):
        if abs(suma - 1) > TOLERANCIA_SUMA:
            errores.append(f"Fila {i} suma {suma:.6g}, debe sumar 1.")
    return errores


def clases_comunicantes(P) -> list[list[int]]:
    """Agrupa los estados que se alcanzan mutuamente (algoritmo de Warshall)."""
    n = len(P)
    alcanza = (np.array(P) > 0) | np.eye(n, dtype=bool)
    for k in range(n):
        alcanza |= np.outer(alcanza[:, k], alcanza[k, :])
    mutuos = alcanza & alcanza.T

    clases = {tuple(np.flatnonzero(fila).tolist()) for fila in mutuos}
    return sorted(list(clase) for clase in clases)


def _periodo(P, clase: list[int]) -> int:
    """MCD de nivel[u] + 1 - nivel[v] por cada arista u -> v de la clase, con niveles de un BFS."""
    nivel = {clase[0]: 0}
    cola = deque([clase[0]])
    periodo = 0
    while cola:
        u = cola.popleft()
        for v in clase:
            if P[u, v] > 0:
                if v not in nivel:
                    nivel[v] = nivel[u] + 1
                    cola.append(v)
                periodo = gcd(periodo, nivel[u] + 1 - nivel[v])
    return periodo


def analizar_cadena(P) -> Analisis:
    """La cadena converge si tiene exactamente una clase cerrada y esta es aperiódica."""
    P = np.array(P, dtype=float)
    clases = clases_comunicantes(P)
    cerradas = [c for c in clases if not np.delete(P[c], c, axis=1).any()]
    periodo = _periodo(P, cerradas[0]) if len(cerradas) == 1 else None
    return Analisis(clases, cerradas, periodo, periodo == 1)


def distribucion_estacionaria(P) -> np.ndarray:
    """Resuelve pi P = pi con suma 1. El sistema es sobredeterminado, por eso mínimos cuadrados."""
    P = np.array(P, dtype=float)
    n = len(P)
    A = np.vstack([P.T - np.eye(n), np.ones(n)])
    b = np.append(np.zeros(n), 1)
    pi = np.linalg.lstsq(A, b, rcond=None)[0]
    return np.clip(pi, 0, None)  # quita negativos del orden de 1e-16 por redondeo


def distancia_tv(mu, nu, axis=None):
    """Distancia de variación total: mitad de la suma de diferencias absolutas."""
    return 0.5 * np.abs(np.asarray(mu) - np.asarray(nu)).sum(axis=axis)


def mixing_time(P, epsilon=0.25, max_pasos=100_000) -> Mezcla:
    """Primer t con d(t) <= epsilon, donde d(t) es la peor distancia entre estados iniciales."""
    P = np.array(P, dtype=float)
    pi = distribucion_estacionaria(P)
    potencia = np.eye(len(P))
    distancias = []
    for t in range(max_pasos + 1):
        distancias.append(float(distancia_tv(potencia, pi, axis=1).max()))
        if distancias[-1] <= epsilon + TOLERANCIA_REDONDEO:
            return Mezcla(t, distancias)
        potencia = potencia @ P
    return Mezcla(None, distancias)


def evolucion_exacta(P, estado_inicial: int, pasos: int) -> np.ndarray:
    """Distribución teórica de cada paso (filas) si la cadena arranca en estado_inicial."""
    P = np.array(P, dtype=float)
    evolucion = np.zeros((pasos + 1, len(P)))
    evolucion[0, estado_inicial] = 1
    for t in range(pasos):
        evolucion[t + 1] = evolucion[t] @ P
    return evolucion


def simular(P, estado_inicial: int, caminantes: int, pasos: int, semilla=None) -> np.ndarray:
    """Monte Carlo: devuelve la distribución empírica de los caminantes en cada paso."""
    P = np.array(P, dtype=float)
    n = len(P)
    rng = np.random.default_rng(semilla)
    acumulada = P.cumsum(axis=1)
    acumulada /= acumulada[:, -1:]  # asegura que la última columna sea exactamente 1

    estados = np.full(caminantes, estado_inicial)
    empirica = np.zeros((pasos + 1, n))
    empirica[0, estado_inicial] = 1
    for t in range(1, pasos + 1):
        azar = rng.random(caminantes)[:, None]
        estados = (azar >= acumulada[estados]).sum(axis=1)
        empirica[t] = np.bincount(estados, minlength=n) / caminantes
    return empirica


def segundo_valor_propio(P) -> float:
    """Módulo del segundo mayor valor propio: d(t) decae aproximadamente como |λ₂|^t."""
    return float(np.sort(np.abs(np.linalg.eigvals(np.array(P, dtype=float))))[-2])


def grafo_dot(P, clases_cerradas: list[list[int]]) -> str:
    """Grafo de transiciones en formato DOT: clases cerradas con doble círculo y color,
    flechas más gruesas cuanto más probable es la transición."""
    P = np.array(P, dtype=float)
    cerrados = {estado for clase in clases_cerradas for estado in clase}
    lineas = ["digraph {", "rankdir=LR;", 'bgcolor="transparent";', "node [shape=circle];"]
    lineas += [
        f'E{i + 1} [peripheries=2, style=filled, fillcolor="#DCE6F1"];' if i in cerrados
        else f"E{i + 1} [peripheries=1];"
        for i in range(len(P))
    ]
    lineas += [
        f'E{i + 1} -> E{j + 1} [label="{P[i, j]:.3g}", penwidth={1 + 3 * P[i, j]:.2f}];'
        for i, j in zip(*np.nonzero(P))
    ]
    return "\n".join(lineas + ["}"])


def clasificar_lluvia(lluvia_mm, ligera=1.0, fuerte=10.0) -> np.ndarray:
    """0 = seco, 1 = lluvia ligera, 2 = lluvia fuerte, según los milímetros del día."""
    return np.digitize(lluvia_mm, [ligera, fuerte])


def estimar_matriz(estados, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Estima P contando cuántas veces cada estado fue seguido por cada otro al día siguiente."""
    estados = np.asarray(estados)
    conteos = np.zeros((n, n), dtype=int)
    np.add.at(conteos, (estados[:-1], estados[1:]), 1)
    totales = conteos.sum(axis=1, keepdims=True)
    sin_datos = np.flatnonzero(totales == 0)
    if len(sin_datos):
        raise ValueError(f"El estado {sin_datos[0] + 1} no tiene datos para estimar su fila.")
    return conteos / totales, conteos


def frecuencia_a_k_pasos(estados, origen: int, k: int, n: int) -> np.ndarray:
    """Distribución observada del estado k días después de los días que estaban en origen."""
    estados = np.asarray(estados)
    siguientes = estados[k:][estados[:-k] == origen]
    return np.bincount(siguientes, minlength=n) / len(siguientes)


# Barajado de cartas: el riffle (cortar en dos montones y entrelazarlos) como cadena de Markov


def subidas(orden) -> int:
    """Secuencias ascendentes del mazo: 1 + veces que la carta v + 1 quedó antes que la carta v."""
    posicion = {carta: i for i, carta in enumerate(orden)}
    return 1 + sum(posicion[v + 1] < posicion[v] for v in range(1, len(orden)))


def eulerianos(n: int) -> list[int]:
    """Cuántos órdenes de n cartas tienen 1, 2, ..., n secuencias ascendentes (números eulerianos)."""
    fila = [1]
    for m in range(2, n + 1):
        fila = [(i + 1) * (fila[i] if i < len(fila) else 0) + (m - i) * (fila[i - 1] if i else 0) for i in range(m)]
    return fila


def matriz_riffle(n: int) -> tuple[np.ndarray, list[tuple]]:
    """Matriz de una barajada riffle (modelo de Gilbert, Shannon y Reeds) sobre los n! órdenes del mazo.

    Un riffle deja el mazo igual con probabilidad (n + 1) / 2^n, en cualquier orden con dos secuencias
    ascendentes con probabilidad 1 / 2^n y nunca en otro orden.
    """
    ordenes = list(permutations(range(1, n + 1)))
    indice = {orden: i for i, orden in enumerate(ordenes)}
    P = np.zeros((len(ordenes), len(ordenes)))
    for i, desde in enumerate(ordenes):
        for hacia in ordenes:
            r = subidas([desde.index(carta) + 1 for carta in hacia])
            P[i, indice[hacia]] = (n + 1) / 2**n if r == 1 else 1 / 2**n if r == 2 else 0
    return P, ordenes


def distribucion_subidas(n: int, k: int) -> np.ndarray:
    """Probabilidad de que tras k riffles el mazo tenga 1, 2, ..., n secuencias ascendentes (Bayer y Diaconis)."""
    a = 2**k
    return np.array([float(Fraction(e * comb(a + n - r, n), a**n)) for r, e in enumerate(eulerianos(n), 1)])


def distancia_barajado(n: int, k: int) -> float:
    """Distancia de variación total exacta entre k riffles de n cartas y un mazo perfectamente mezclado."""
    a, uniforme = 2**k, Fraction(1, factorial(n))
    total = sum(e * abs(Fraction(comb(a + n - r, n), a**n) - uniforme) for r, e in enumerate(eulerianos(n), 1))
    return float(total / 2)


def leer_experimento(texto: str) -> tuple[list[tuple[int, list[int]]], list[str]]:
    """Lee líneas «barajadas: orden», por ejemplo «2: 3 1 5 2 4». Devuelve los ensayos y los errores."""
    ensayos, errores, n = [], [], None
    for numero, linea in enumerate(texto.splitlines(), 1):
        if not linea.strip():
            continue
        partes = re.fullmatch(r"\s*(\d+)\s*:\s*([\d\s,]+?)\s*", linea)
        if not partes:
            errores.append(f"Línea {numero}: escribe «barajadas: orden», por ejemplo «2: 3 1 5 2 4».")
            continue
        orden = [int(c) for c in re.split(r"[\s,]+", partes.group(2))]
        n = n or len(orden)
        if sorted(orden) != list(range(1, n + 1)):
            errores.append(f"Línea {numero}: debe tener cada número del 1 al {n} una sola vez.")
            continue
        ensayos.append((int(partes.group(1)), orden))
    return ensayos, errores


def barajadas_equivalentes(distribucion_observada, n: int, max_barajadas: int = 12) -> int:
    """Número de riffles del modelo cuya distribución de secuencias ascendentes se parece más a la observada."""
    distancias = [distancia_tv(distribucion_observada, distribucion_subidas(n, k)) for k in range(1, max_barajadas + 1)]
    return int(np.argmin(distancias)) + 1


def secuencias_ascendentes(orden) -> list[int]:
    """A qué secuencia ascendente pertenece cada carta, en el orden del mazo (sirve para colorearlas)."""
    posicion = {carta: i for i, carta in enumerate(orden)}
    secuencia, numero = {}, 1
    for v in range(1, len(orden) + 1):
        if v > 1 and posicion[v] < posicion[v - 1]:
            numero += 1
        secuencia[v] = numero
    return [secuencia[carta] for carta in orden]


def riffle(mazo, rng) -> tuple[list, int]:
    """Un riffle del modelo de Gilbert, Shannon y Reeds: corte binomial y cada carta cae del montón
    elegido con probabilidad proporcional a su tamaño. Devuelve el mazo nuevo y cuántas cartas quedaron arriba."""
    corte = int(rng.binomial(len(mazo), 0.5))
    arriba, abajo, resultado = list(mazo[:corte]), list(mazo[corte:]), []
    while arriba or abajo:
        monton = arriba if rng.random() < len(arriba) / (len(arriba) + len(abajo)) else abajo
        resultado.append(monton.pop(0))
    return resultado, corte


def simular_experimento(n: int, barajadas, intentos: int, semilla=None) -> str:
    """Resultados de prueba con el formato «barajadas: orden», generados con el modelo."""
    rng = np.random.default_rng(semilla)
    lineas = []
    for k in barajadas:
        for _ in range(intentos):
            mazo = list(range(1, n + 1))
            for _ in range(k):
                mazo, _ = riffle(mazo, rng)
            lineas.append(f"{k}: " + " ".join(map(str, mazo)))
    return "\n".join(lineas)
