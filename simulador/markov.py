"""Lógica de cadenas de Markov: validación, convergencia, estado estable y mixing time."""
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from math import gcd

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
    """Grafo de transiciones en formato DOT; las clases cerradas llevan doble círculo."""
    P = np.array(P, dtype=float)
    cerrados = {estado for clase in clases_cerradas for estado in clase}
    lineas = ["digraph {", "rankdir=LR;", 'bgcolor="transparent";', "node [shape=circle];"]
    lineas += [f"E{i + 1} [peripheries={2 if i in cerrados else 1}];" for i in range(len(P))]
    lineas += [f'E{i + 1} -> E{j + 1} [label="{P[i, j]:.3g}"];' for i, j in zip(*np.nonzero(P))]
    return "\n".join(lineas + ["}"])
