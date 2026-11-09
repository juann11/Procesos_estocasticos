# Guía de exposición: Simulador de cadenas de Markov

Exposición por Teams el 11 de noviembre de 2026. Ambos deben estar presentes y poder responder sobre el programa (vale 1.0 de los 5 puntos).

Material:

- `documentos/Diapositivas.pdf`: la presentación.
- `documentos/Notas_del_orador.md`: qué decir en cada diapositiva.
- Esta guía: preparación, demo y preguntas.

## 1. Antes de empezar (15 minutos antes)

1. Abran una terminal en la carpeta del proyecto y corran `uv run python -m streamlit run simulador/app.py`. El navegador se abre solo en `http://localhost:8501`. La primera vez del día puede tardar más de 30 segundos, por eso se abre antes.
2. Si sale `ConnectionResetError [WinError 10054]` en rojo en la terminal, ignórenlo: es un aviso de Python en Windows y no afecta la app.
3. Si dice que el puerto 8501 está ocupado, cierren la otra terminal con `Ctrl+C` o usen `uv run python -m streamlit run simulador/app.py --server.port 8502`.
4. Dejen lista otra terminal con `uv run python -m pytest` por si el profesor pide ver las pruebas: deben salir **48 passed**.
5. En Teams compartan la **ventana** del navegador o la pantalla completa, y suban el zoom del navegador si se ve pequeño (`Ctrl` + `+`).
6. Tengan el PDF de las diapositivas abierto como respaldo por si falla la app.

## 2. Reparto sugerido

Es una propuesta: ajústenla a quien domine mejor cada tema. Lo importante es que **los dos** sepan responder de todo.

| Parte | Diapositivas | Quién |
|---|---|---|
| Presentación, qué hace, construcción, página, conceptos | 1 a 6 | Juan José |
| Ítem 1 y 2: entrada, criterio, clases y período | 7 a 10 | Juan José |
| Ítem 3 y 4: π, mixing time, algoritmo, ejemplos, animación, velocidad | 11 a 17 | Geronimo |
| Ítem 5, validación y límites | 18 a 22 | Geronimo |
| Demostración en vivo | 23 | Uno maneja la app y el otro explica |
| Conclusiones y preguntas | 24 a 26 | Ambos |

## 3. Demo en vivo, paso a paso

El ejemplo se elige en la **barra lateral**, a la izquierda. Ahí también está ε.

| Paso | Qué hacer | Qué debe aparecer |
|---|---|---|
| 1 | Elegir **Regular (2 estados)** | Tarjetas: estable Sí, mixing time 2, \|λ₂\| 0.4000, estado más probable E1. π = (0.8333, 0.1667) |
| 2 | En "Animación de convergencia", elegir E2 y darle **▶ Reproducir** | La barra azul alcanza a la naranja; en t = 2 la distancia es 0.1333 |
| 3 | Cambiar ε a 0.01 en la barra lateral | Mixing time pasa a 5 |
| 4 | Abrir un **"¿Qué significa?"** | Explicación corta de la sección |
| 5 | Elegir **Periódica (2 estados)** | Tarjetas: estable No, clases cerradas 1, período 2 |
| 6 | Elegir **Dos estados absorbentes** | Tarjetas: estable No, clases cerradas 2; en el grafo E1 y E3 rellenos en azul |
| 7 | Elegir **Personalizada** | Tabla de 3 × 3 con 1/3, mixing time 1 |
| 8 | Si el profe da una matriz, escribirla con **doble clic** en cada casilla | Si tiene tercios, escribir `1/3`, no `0.3333` |

Si se equivocan al escribir, la app dice exactamente qué casilla o qué fila está mal.

## 4. Preguntas probables y cómo responderlas

### Sobre la teoría

**¿Qué es el mixing time?**
Respondan con sus palabras, como en el apartado 1.1 del reporte: cuántos pasos necesita la cadena para olvidar su estado inicial y quedar lo bastante cerca de π. "Lo bastante cerca" lo define ε.

**¿Por qué usan la distancia de variación total?**
Porque mide la mayor diferencia de probabilidad que dos distribuciones le pueden asignar a un mismo evento. Es la distancia estándar para el mixing time en Levin, Peres y Wilmer. Se calcula como ½ Σ |μ(x) − ν(x)|.

**¿Por qué toman el máximo sobre los estados iniciales?**
Porque el mixing time no debe depender de dónde arranque la cadena: se garantiza para el peor caso. En el ejemplo de 2 estados, el peor arranque es E2.

**¿Por qué ε = 1/4?**
Es la convención del libro. Con ese valor, cada mixing time adicional reduce la distancia al menos a la mitad. El usuario puede cambiarlo entre 0.001 y 0.5.

**¿d(t) puede subir?**
No. Aplicar P a dos distribuciones nunca las aleja, y π no cambia al aplicar P. Por eso el primer t que cumple d(t) ≤ ε es el mínimo, y la gráfica lo muestra: la curva sigue bajando después del mixing time.

**¿Cuándo hay estado estable?**
Cuando hay exactamente una clase cerrada y esa clase es aperiódica. Los estados transitorios no estorban.

**¿En qué se diferencia de pedir una matriz regular?**
Una matriz regular, con alguna potencia de entradas todas positivas, no puede tener estados transitorios. Nuestro criterio es más general: la cadena "Absorbente con transitorios" no es regular y sí converge, a π = (0, 0, 1).

**¿Qué es el período y cómo lo calculan?**
Es el MCD de las longitudes de los ciclos que regresan a un estado. El programa recorre la clase con BFS, asigna niveles y calcula el MCD de nivel(u) + 1 − nivel(v) en cada flecha u → v. Ejemplo: [[0, 1], [1, 0]] solo tiene ciclos de longitud 2, así que su período es 2 y oscila.

**¿La cadena periódica no tiene π?**
Sí tiene: π = (0.5, 0.5). Pero no converge a ella: alterna entre (1, 0) y (0, 1). Por eso el programa dice que no se alcanza el estado estable.

**¿Y con dos clases cerradas?**
Hay varias distribuciones estacionarias posibles y el resultado depende de dónde empiece la cadena, así que no hay un único estado estable.

**¿Qué es |λ₂|?**
El módulo del segundo mayor valor propio de P. d(t) decae aproximadamente como |λ₂|ᵗ. En el ejemplo de 2 estados, los valores propios son 1 y 0.4, y por eso d(t) = (5/6) · 0.4ᵗ.

### Sobre el programa

**¿Cómo calculan π?**
Resolviendo πP = π junto con la suma igual a 1. Son n + 1 ecuaciones con n incógnitas, y se resuelven por mínimos cuadrados con `numpy.linalg.lstsq`. Otra opción válida sería el vector propio izquierdo de valor propio 1.

**¿Cómo agrupan las clases?**
Con el algoritmo de Warshall calculan qué estados alcanzan a cuáles; dos estados están en la misma clase si cada uno alcanza al otro.

**¿Qué pasa si la cadena nunca baja de ε?**
El programa se detiene a los 100 000 pasos y avisa que no se alcanzó ε, en vez de inventar un número.

**¿Cómo funciona la simulación?**
Cada caminante sortea un número u entre 0 y 1, y el tramo de la fila acumulada de P donde cae decide su siguiente estado. Contando caminantes por estado se obtiene la distribución empírica.

**¿Por qué la curva simulada no llega a 0?**
Por el ruido del muestreo, que baja como 1/√N: con 10 veces más caminantes el ruido baja unas 3 veces (0.0560, 0.0193, 0.0061, 0.0016).

**¿Por qué la semilla es fija?**
Para que la simulación sea repetible y se pueda verificar.

**¿Por qué aceptan fracciones?**
Porque 0.3333 tres veces suma 0.9999 y la fila se rechazaría; 1/3 tres veces suma exactamente 1.

**¿Cómo saben que el programa está bien?**
Por tres caminos: 48 pruebas automáticas que se escribieron antes del código; dos cadenas calculadas a mano que coinciden (mixing time 2 y 5), y un experimento en el que rompimos el código a propósito 19 veces y las pruebas detectaron 16. Las otras 3 eran protecciones contra redondeo casi imposibles de provocar.

**¿Por qué separaron markov.py y app.py?**
Para que la matemática no dependa de la interfaz y se pueda probar sola.

## 5. Valores de referencia

| Cadena | ¿Estable? | π | Mixing time (ε = 1/4) | \|λ₂\| |
|---|---|---|---|---|
| Regular (2 estados) | Sí | (0.8333, 0.1667) | 2 | 0.4 |
| Regular (3 estados) | Sí | (0.3, 0.3, 0.4) | 1 | 0.3 |
| Absorbente con transitorios | Sí | (0, 0, 1) | 5 | 0.5 |
| Periódica (2 estados) | No, período 2 | — | — | — |
| Dos estados absorbentes | No, 2 clases cerradas | — | — | — |

En la regular de 2 estados: con ε = 0.1 el mixing time es 3, y con ε = 0.01 es 5.
