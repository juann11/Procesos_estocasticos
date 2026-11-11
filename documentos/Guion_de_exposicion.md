# Guion de exposición: Simulador de cadenas de Markov

Qué decir en cada diapositiva, en el orden de la presentación. Está escrito para leerlo en voz alta o repasarlo antes; no hace falta memorizarlo palabra por palabra, sino la idea de cada bloque.

- **JJ** = Juan José Ospina · **GG** = Geronimo Gaviria
- Duración estimada: unos 23 minutos de exposición y 6 de demo. Los anexos (28 y 29) solo se usan si hay preguntas.
- Antes de empezar, la app ya debe estar abierta (ver la sección final "Cómo lanzar el programa").

---

## Parte 1. Introducción (JJ)

### 1. Portada · JJ · 30 s

> Buenos días, profesor. Somos Juan José Ospina y Geronimo Gaviria. Les vamos a presentar nuestro simulador de cadenas de Markov: un programa que recibe una matriz estocástica y responde tres preguntas: si la cadena llega a un estado estable, cuál es esa distribución y cuántos pasos tarda en llegar, es decir, el mixing time. Yo voy a presentar la primera parte y Geronimo la parte del mixing time y la simulación.

### 2. Qué hace el programa · JJ · 45 s

> El programa sigue los cinco puntos del enunciado, en el mismo orden. Primero recibe la matriz y la valida. Segundo, decide si se alcanza un estado estable. Tercero, si la respuesta es sí, calcula la distribución estacionaria π. Cuarto, mide el mixing time para la tolerancia ε que elija el usuario. Y quinto, nuestra funcionalidad particular: aplicamos todo a un caso real, el clima de Medellín, con datos de 1096 días; además, simulamos la cadena para comparar el azar con la teoría.
>
> Un detalle importante: si en el paso 2 la cadena no converge, el programa no sigue calculando cosas sin sentido; explica la causa y se detiene.

### 3. Cómo está construido · JJ · 45 s

> Lo hicimos en Python. Usamos NumPy para el álgebra lineal y Streamlit para la interfaz web, que nos permitió tener una página interactiva sin construir un frontend aparte.
>
> El proyecto tiene tres partes: `app.py` y sus dos páginas, el simulador y el caso real; `markov.py`, donde está toda la matemática, y la carpeta de pruebas, con 57 pruebas automáticas. La decisión de diseño más importante es que la matemática no depende de la interfaz: `markov.py` no sabe que existe una página web, y por eso pudimos probar cada cálculo por separado.

### 4. Recorrido por la página · JJ · 45 s

> Así se ve la aplicación. A la izquierda está la barra lateral, donde se elige la matriz, sea un ejemplo o una personalizada, y la tolerancia ε. Arriba, en cuatro tarjetas, están las respuestas principales: si hay estado estable, el mixing time, el segundo valor propio y el estado más probable a largo plazo.
>
> Debajo hay cinco secciones, una por cada ítem del enunciado, y cada una tiene un desplegable "¿Qué significa?" con la explicación teórica. Al final lo vamos a mostrar en vivo.

### 5. Dónde está cada ítem en el código · JJ · 30 s

> Esta tabla es el mapa del código. Cada ítem del enunciado tiene sus funciones en `markov.py`: `leer_matriz` y `validar_matriz` para la entrada; `analizar_cadena` para decidir si hay estado estable; `distribucion_estacionaria` para π; `mixing_time` para el ítem 4, y `simular` para la simulación. Cada función hace una sola cosa y tiene sus propias pruebas. Si quiere ver alguna, la podemos abrir.

### 6. Conceptos que usa el programa · JJ · 60 s

> Antes de entrar a los ítems, repasamos los conceptos que usamos.
>
> Una **matriz estocástica** tiene en la posición i, j la probabilidad de pasar del estado i al estado j, y cada fila suma 1. Una **clase comunicante** es un grupo de estados que pueden alcanzarse entre sí. Una **clase cerrada** es una clase de la que la cadena ya no puede salir. Un **estado transitorio** es uno al que la cadena deja de volver: su probabilidad tiende a cero. El **período** es el máximo común divisor de las longitudes de los caminos que regresan a un estado. Y la **distribución estacionaria** π es la que no cambia al aplicar P.

---

## Parte 2. Ítems 1 y 2 (JJ)

### 7. Ítem 1: entrada de la matriz · JJ · 45 s

> El primer ítem pide solicitar la matriz al usuario. Lo hacemos con una tabla editable de hasta 12 estados.
>
> Cada casilla acepta decimales, con punto o con coma, y también fracciones como 1/3. Esto último es importante: si alguien escribe 0.3333 tres veces, la fila suma 0.9999 y no es estocástica; con 1/3 suma exactamente 1. Antes de calcular validamos que no haya casillas vacías ni negativos y que cada fila sume 1, y si algo falla, el programa señala la fila o la casilla exacta.

### 8. Ítem 2: cuándo hay estado estable · JJ · 60 s

> El ítem 2 es decidir si la cadena alcanza un estado estable. Nuestro criterio es: **exactamente una clase cerrada, y que sea aperiódica**.
>
> Hay tres casos. Si hay una sola clase cerrada con período 1, la cadena olvida dónde empezó y converge. Si la clase cerrada tiene período 2 o más, la cadena oscila y nunca se estabiliza. Y si hay dos o más clases cerradas, el resultado depende de dónde arranque, así que no hay un único estado estable.
>
> Este criterio es más general que pedir una matriz regular, porque acepta estados transitorios: la cadena los abandona y aun así converge.

### 9. Ítem 2: cómo lo decide el programa · JJ · 60 s

> El programa lo decide en cuatro pasos. Primero construye el grafo: hay una flecha de i a j cuando P(i, j) es mayor que cero. Segundo, con el algoritmo de Warshall calcula qué estados alcanzan a cuáles, y agrupa en la misma clase los que se alcanzan mutuamente. Tercero, busca las clases cerradas, que son aquellas de las que no sale ninguna flecha. Y cuarto, calcula el período con un recorrido en anchura.
>
> A la derecha está un grafo real que genera el programa: E1 y E3 son absorbentes, con doble círculo y relleno azul. Como hay dos clases cerradas, el programa dice que no se alcanza un estado estable.

### 10. Ítem 2: el período con dos ejemplos · JJ · 60 s

> Para entender el período, dos ejemplos. A la izquierda, la matriz que intercambia E1 y E2: el único ciclo tiene longitud 2, el período es 2 y la cadena oscila para siempre entre (1, 0) y (0, 1).
>
> A la derecha, una cadena sin autolazos, pero con un ciclo de longitud 2 y otro de longitud 3. El máximo común divisor de 2 y 3 es 1, así que es aperiódica y sí converge. Por eso no basta con mirar la diagonal: un autolazo garantiza aperiodicidad, pero no es necesario. Los dos casos están en nuestras pruebas automáticas.
>
> Con esto termino mi parte; Geronimo sigue con π y el mixing time.

---

## Parte 3. Ítems 3 y 4 (GG)

### 11. Ítem 3: distribución de estado estable · GG · 45 s

> Gracias. Si el ítem 2 dio positivo, calculamos la distribución estacionaria π, que es la que cumple πP = π y cuyas entradas suman 1.
>
> Las ecuaciones de πP = π son dependientes entre sí, por eso agregamos la condición de que π sume 1. Nos queda un sistema de n + 1 ecuaciones con n incógnitas, que resolvemos por mínimos cuadrados con NumPy. Por ejemplo, para la matriz de 2 estados con 0.9 y 0.1 en la primera fila y 0.5 y 0.5 en la segunda, π da 5/6 y 1/6, es decir, 0.8333 y 0.1667.

### 12. Ítem 4: cómo calculamos el mixing time · GG · 75 s

> Ahora el mixing time. Su objetivo es medir cuántos pasos necesita la cadena para olvidar su estado inicial, es decir, para quedar lo bastante cerca de π sin importar dónde empezó.
>
> Para medir qué tan cerca están dos distribuciones usamos la distancia de variación total: la mitad de la suma de las diferencias absolutas. Después de t pasos, cada fila de P a la t es la distribución si la cadena arrancó en ese estado. Tomamos el peor caso entre todos los estados iniciales, y eso es d(t). El mixing time es el primer t en que d(t) es menor o igual que la tolerancia ε.
>
> Usamos ε = 1/4 por defecto, que es la convención del libro de Levin, Peres y Wilmer, y el usuario la puede cambiar.

### 13. Ítem 4: el algoritmo en código · GG · 45 s

> En código es un ciclo sencillo. Empezamos con la matriz identidad, que es P a la cero. En cada paso calculamos la distancia de cada fila a π y nos quedamos con la mayor. Si ya es menor o igual que ε, devolvemos ese t; si no, multiplicamos por P y repetimos.
>
> Como d(t) nunca aumenta, el primer t que cumple es el mínimo. Y si la cadena no baja de ε en 100 000 pasos, el programa lo avisa en vez de inventar un número.

### 14. Ítem 4: ejemplo resuelto a mano · GG · 45 s

> Lo verificamos a mano con la misma matriz de 2 estados. Ahí d(t) es 5/6 por 0.4 a la t. En t = 0 vale 0.8333; en t = 1, 0.3333, todavía mayor que 0.25; en t = 2, 0.1333, que ya está por debajo. Entonces el mixing time es 2, que es exactamente lo que da el programa.
>
> En la gráfica, la línea punteada es ε y la línea naranja marca el mixing time. Dejamos que la curva siga después para mostrar que nunca vuelve a subir.

### 15. Ítem 4: el mismo ejemplo, paso a paso · GG · 45 s

> Aquí está el detalle de cada paso. En t = 1, si la cadena arrancó en E1 está a 0.0667 de π, pero si arrancó en E2 está a 0.3333. Ese es el peor caso, y es el que cuenta.
>
> Por ejemplo, la distancia de la fila E2 es la mitad de |0.5 − 0.8333| más |0.5 − 0.1667|, que da 0.3333. Tomamos el peor caso porque el mixing time tiene que valer para cualquier estado inicial.

### 16. Ítem 4: la convergencia en movimiento · GG · 45 s

> Esto mismo se puede ver animado en la página. Elegimos E2 como estado inicial, porque es el peor caso. La barra azul es la distribución en el paso t y la naranja es π. Al principio toda la probabilidad está en E2, y con cada paso la azul se va pareciendo a la naranja: la distancia baja de 0.8333 a 0.3333 y luego a 0.1333. En t = 2 ya está por debajo de ε: eso es el mixing time. Lo vamos a mostrar en la demo.

### 17. Ítem 4: qué explica la velocidad · GG · 45 s

> ¿Por qué unas cadenas mezclan más rápido que otras? Lo explica el segundo valor propio de P en módulo, |λ₂|: d(t) decae aproximadamente como |λ₂| a la t. Entre más cerca de 1, más lenta es la mezcla.
>
> En la tabla se ve: con |λ₂| = 0.3 el mixing time es 1; con 0.4, es 2, y con 0.5, es 5. Por eso en el ejemplo aparecía 0.4 a la t: 0.4 es justamente el segundo valor propio de esa matriz.

---

## Parte 4. Ítem 5 y validación (GG)

### 18. Ítem 5: simulación Monte Carlo · GG · 45 s

> El ítem 5 pedía una funcionalidad propia. La nuestra es una simulación Monte Carlo: en vez de calcular con álgebra, soltamos miles de caminantes en la cadena y vemos a dónde llegan.
>
> Con 10 000 caminantes y 20 pasos en la cadena de 2 estados, la simulación da 0.8339 y 0.1661, prácticamente la misma π que calculamos: 0.8333 y 0.1667. Es una comprobación independiente, porque no usa el sistema lineal.

### 19. Ítem 5: cómo salta cada caminante · GG · 45 s

> ¿Cómo decide cada caminante a dónde ir? Sorteamos un número u entre 0 y 1. Si está en E1, la fila es 0.9 y 0.1: si u es menor que 0.9, se queda en E1, y si es mayor, pasa a E2. Por ejemplo, con u = 0.37 se queda y con u = 0.95 pasa a E2.
>
> En código se usa la fila acumulada y se hace para todos los caminantes a la vez, por eso 100 000 caminantes corren rápido.

### 20. Ítem 5: el efecto de los caminantes · GG · 45 s

> La simulación nunca llega exactamente a cero, porque tiene ruido de muestreo. Ese ruido baja como uno sobre la raíz de N: cada vez que multiplicamos los caminantes por 10, el ruido baja unas 3 veces. Con 100 caminantes la distancia es 0.056, y con 100 000 baja a 0.0016. Esto también lo podemos mostrar moviendo el control de caminantes.

## Parte 4b. Caso real: el clima de Medellín (JJ)

Esta es la parte que hace único el trabajo: el mismo método aplicado a datos reales.

### 21. Caso real: ¿en cuántos días se olvida el clima de hoy? · JJ · 60 s

> Como funcionalidad particular quisimos llevar el simulador a algo real. En el simulador la matriz la escribe el usuario; aquí la sacamos de datos: la lluvia diaria de Medellín de 2023 a 2025, 1096 días, de la API de clima histórico de Open-Meteo.
>
> Cada día lo clasificamos en uno de tres estados: seco, si llovió menos de 1 milímetro; lluvia ligera, entre 1 y 10, y lluvia fuerte, de 10 en adelante. Así, la historia del clima se vuelve una cadena de Markov, y la pregunta del taller se vuelve concreta: ¿en cuántos días se olvida el clima de hoy?

### 22. Caso real: la matriz que salió de los datos · JJ · 60 s

> Para estimar P contamos, para cada tipo de día, qué tipo de día vino después. Por ejemplo, después de un día de lluvia fuerte, el siguiente fue también de lluvia fuerte el 45.9 % de las veces y seco solo el 7.4 %. Eso es el ítem 1, pero con una matriz que sale de la realidad.
>
> Con el ítem 2 vemos que sí hay estado estable: los tres tipos de día se comunican y la cadena es aperiódica. Y el ítem 3 nos da π: a largo plazo Medellín tiene 29.4 % de días secos, 47.2 % de lluvia ligera y 23.4 % de lluvia fuerte, prácticamente lo mismo que pasó en los tres años.

### 23. Caso real: el clima recuerda más que el modelo · JJ · 75 s

> El ítem 4 responde la pregunta: con ε = 1/4 el mixing time es 2 días. Según la cadena, después de un par de días ya casi no importa si hoy llovió.
>
> Pero aquí está lo más interesante: lo comparamos con lo que pasó de verdad. Al día siguiente el modelo coincide exacto, porque P se estimó con esos pares de días. Pero 5 días después de un día de lluvia fuerte, el modelo predice 24 % de lluvia fuerte y en la realidad fue 32 %. El clima real recuerda más, porque hay temporadas de lluvia y temporadas secas que duran semanas, y una cadena que solo mira el día anterior no las capta. Entonces el mixing time del modelo es un límite inferior: el clima real tarda un poco más en olvidarse.
>
> Ahora Geronimo cierra con cómo validamos todo.

### 24. Cómo validamos el programa · GG · 45 s

> Para asegurarnos de que el programa está bien, hicimos tres cosas. Primero, 57 pruebas automáticas, escritas antes del código: 45 para la matemática y 12 para las dos páginas. Segundo, calculamos dos cadenas a mano y coincidieron con el programa. Y tercero, para comprobar que las pruebas sirven, metimos 19 errores a propósito en el código: las pruebas detectaron 16. Los otros 3 son protecciones contra redondeo que son casi imposibles de provocar. Ese experimento además nos mostró un hueco en las pruebas del período, que corregimos.

### 25. Alcance y límites del programa · GG · 30 s

> También tenemos claros los límites: hasta 12 estados; el grafo se dibuja hasta 8, porque con más es ilegible; el mixing time se busca hasta 100 000 pasos; ε entre 0.001 y 0.5, y la simulación hasta 1000 pasos. El programa trabaja con cadenas de estados finitos y probabilidades que no cambian con el tiempo.
>
> Ahora lo mostramos funcionando.

---

## Parte 5. Demostración en vivo (ambos)

### 26. Demostración en vivo · JJ maneja la app y GG explica · 5 min

Cambien a la ventana del navegador con la app. Sigan este orden:

| Paso | Qué hacer | Qué decir |
|---|---|---|
| 1 | En la barra lateral, elegir **Regular (2 estados)** | "Esta es la matriz del ejemplo. Arriba, las tarjetas: sí hay estado estable, mixing time 2, segundo valor propio 0.4 y estado más probable E1." |
| 2 | Bajar al mapa de calor y la sección 2 | "El mapa de calor muestra la matriz; entre más oscuro, más probable. Aquí dice que hay una única clase cerrada y aperiódica." |
| 3 | Abrir un **"¿Qué significa?"** | "Cada sección tiene su explicación." |
| 4 | En "Animación de convergencia", elegir **E2** y darle **▶ Reproducir** | "La barra azul arranca toda en E2 y se va pareciendo a π." |
| 5 | En la barra lateral, cambiar ε a **0.01** | "Si somos más exigentes, el mixing time sube a 5." Volver a 0.25. |
| 6 | Bajar a la simulación y mover **Caminantes** | "Con más caminantes, la curva simulada se pega a la teórica." |
| 7 | Elegir **Periódica (2 estados)** | "Esta oscila: período 2. El programa explica que no converge y se detiene." |
| 8 | Elegir **Dos estados absorbentes** | "Aquí hay dos clases cerradas, E1 y E3, rellenas en azul en el grafo. El resultado depende de dónde empiece." |
| 9 | Elegir **Personalizada** | "Profesor, si quiere nos da una matriz y la probamos." |
| 10 | En el menú de la izquierda, abrir **Caso real: clima de Medellín** | "Aquí está el mismo método con datos reales. La matriz salió de 1096 días de lluvia." Bajar hasta la última gráfica: "El modelo olvida en 2 días, pero la realidad recuerda más." |
| 11 | Cambiar el umbral de lluvia fuerte | "Si cambiamos qué cuenta como lluvia fuerte, la matriz y π se recalculan solas." |

Consejos:

- Para cambiar una casilla, **doble clic**. Si la matriz tiene tercios, escriban `1/3`, no `0.3333`.
- Si escriben mal un valor, la app dice exactamente qué casilla o qué fila falla: léanlo en voz alta y corríjanlo.
- Si el profesor da una matriz con tercios y ustedes escribieron decimales, ese es el momento para explicar por qué aceptan fracciones.

---

## Parte 6. Cierre (ambos)

### 27. Conclusiones · JJ y GG · 45 s

> **JJ:** Para cerrar: el programa diagnostica si hay estado estable y, cuando no lo hay, explica por qué.
>
> **GG:** Calcula π y el mixing time, y lo comprobamos con casos resueltos a mano.
>
> **JJ:** Verifica la teoría con una simulación independiente.
>
> **GG:** Y lo aplicamos a datos reales: el clima de Medellín se olvida en unos 2 días según el modelo, aunque en la realidad recuerda un poco más. Así cubrimos los cinco ítems del enunciado.
>
> **GG:** Muchas gracias. ¿Tienen alguna pregunta?

### 28 y 29. Anexos · solo si preguntan

No se presentan. Si el profesor pregunta algo que está en los anexos, vayan a esa diapositiva y respondan con ella:

- **28, sobre el método:** por qué la distancia de variación total, por qué ε = 1/4, por qué d(t) no sube y la diferencia entre una cadena periódica y una reducible.
- **29, sobre el programa:** por qué mínimos cuadrados, por qué iterar potencias, por qué semilla fija y por qué aceptar fracciones.

Las notas del orador de cada diapositiva, dentro del PowerPoint, tienen más detalle para responder.

---

## Cómo lanzar el programa

Háganlo **15 minutos antes**, no durante la exposición:

1. Abran una terminal (PowerShell) en la carpeta del proyecto.
2. Corran:

   ```bash
   uv run python -m streamlit run simulador/app.py
   ```

3. Abran `http://localhost:8501` en el navegador. La primera vez del día puede tardar más de 30 segundos. También está la versión en línea: https://markov-medellin.streamlit.app
4. Si sale en rojo `ConnectionResetError [WinError 10054]`, ignórenlo: es un aviso de Windows y no afecta la app.
5. Si dice que el puerto 8501 está ocupado, cierren la otra terminal con `Ctrl+C`, o usen otro puerto:

   ```bash
   uv run python -m streamlit run simulador/app.py --server.port 8502
   ```

6. Si el profesor pide ver las pruebas, en otra terminal:

   ```bash
   uv run python -m pytest
   ```

   Debe decir **57 passed**.

En Teams, compartan la pantalla completa para poder pasar entre las diapositivas y el navegador. Tengan abierto `Diapositivas.pptx` como respaldo.
