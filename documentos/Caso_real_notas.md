# Notas del orador: Caso real: el clima de Medellín

## 1. ¿En cuántos días se olvida el clima de hoy?

Presentarnos. La frase de entrada: "Todos hemos notado que en Medellín, cuando empieza a llover, suele seguir lloviendo unos días. Quisimos medir eso con matemáticas: ¿cuántos días dura la memoria del clima?". Aclarar que es el mismo trabajo del taller, pero aplicado a datos reales.

## 2. La idea: llevar el taller a datos reales

Explicar que no cambiamos el taller: seguimos haciendo los cinco ítems (matriz, estado estable, distribución estable, mixing time y una funcionalidad propia). Lo que cambia es de dónde sale la matriz. En vez de inventar números, los contamos en la realidad. Eso le da sentido a cada resultado: π deja de ser un vector y pasa a ser "qué porcentaje de días llueve en Medellín", y el mixing time pasa a ser "cuántos días dura la memoria del clima".

## 3. Los datos: tres años de lluvia en Medellín

Los datos son la lluvia diaria de Medellín del 1 de enero de 2023 al 31 de diciembre de 2025, 1096 días, de la API de clima histórico de Open-Meteo. Los guardamos en el proyecto para que la app funcione sin internet. En palabras sencillas: es como un calendario de tres años en el que pintamos cada día según cuánto llovió. Cada barra de la gráfica es un día. Usamos 1 mm como umbral de día lluvioso porque es el umbral usual, y 10 mm para lluvia fuerte. En la app esos umbrales se pueden cambiar y todo se recalcula.

## 4. Ítem 1: la matriz se estima contando

Este es el paso clave y lo que nos diferencia: no inventamos la matriz, la contamos. Recorrimos los 1096 días y, para cada día, anotamos qué tipo de día vino después. La tabla muestra esos conteos. Por ejemplo, hubo 257 días de lluvia fuerte con día siguiente; de esos, 118 fueron seguidos por otro aguacero, 120 por lluvia ligera y solo 19 por un día seco. Para convertir conteos en probabilidades se divide cada fila entre su total: 118 entre 257 da 0.459. En palabras sencillas: la matriz es una tabla de "qué suele venir después".

## 5. Ítem 2: la cadena del clima sí se estabiliza

Le aplicamos el mismo criterio del simulador: hay estado estable si hay exactamente una clase cerrada y es aperiódica. Aquí los tres tipos de día forman una sola clase, porque desde cualquier tipo de día se puede llegar a cualquier otro. Y es aperiódica porque cada tipo de día puede repetirse al día siguiente: hay autolazos. En palabras sencillas: el clima no está obligado a seguir un ciclo fijo como "seco, lluvia, seco, lluvia", así que termina en un patrón estable sin importar cómo empezó. Lectura de la matriz: después de un aguacero, mañana hay 45.9 % de otro aguacero y solo 7.4 % de día seco.

## 6. Ítem 3: así es el clima de Medellín a largo plazo

El ítem 3 nos da π, la distribución estacionaria, calculada igual que en el simulador: resolviendo πP = π con la condición de que sume 1. Da 29.4 % de días secos, 47.2 % de lluvia ligera y 23.4 % de lluvia fuerte. La frecuencia real en los tres años fue 29.3 %, 47.3 % y 23.4 %. En palabras sencillas: π es el promedio a largo plazo; si escoges un día cualquiera de Medellín al azar, sin saber nada más, hay más o menos 29 de 100 posibilidades de que esté seco. Que coincida con la realidad es una primera validación del modelo.

## 7. Ítem 4: el clima de hoy se olvida en 2 días

El ítem 4 responde la pregunta del trabajo. Calculamos d(t), la distancia en el peor caso entre lo que predice la cadena desde cada tipo de día y π, igual que en el simulador. En el día 1 vale 0.30, todavía mayor que 0.25; en el día 2 vale 0.14, ya por debajo, así que con ε = 1/4 el mixing time es 2 días. Si somos más exigentes, con ε = 0.1 son 3 días y con ε = 0.01 son 6. En palabras sencillas: es cuánto dura la memoria del clima. Si hoy cayó un aguacero, mañana es más probable que llueva; pero después de unos días esa información ya no sirve y es como adivinar con el promedio. El segundo valor propio es 0.468, que explica la velocidad.

## 8. La prueba: el modelo frente a lo que pasó

Esta es la parte que nadie más tiene: pusimos a prueba el modelo con la realidad. Buscamos todos los días de lluvia fuerte y miramos qué pasó de verdad 1, 2, 3 y hasta 10 días después. La línea azul es lo que predice la cadena, P a la k, y la naranja lo que pasó. Al día siguiente coinciden exacto, porque la matriz se estimó justo con esos pares de días. Pero después se separan: 5 días después de un aguacero, el modelo predice 24.2 % de lluvia fuerte y en la realidad fue 31.9 %. Y pasa lo mismo al revés: después de un día seco, en la realidad caen menos aguaceros de los que predice el modelo. La línea punteada es π.

## 9. Lo que aprendimos

Conclusión del caso real. El modelo de Markov acierta en lo importante: el reparto de días a largo plazo y el clima del día siguiente. Su límite es que solo mira el día anterior, y el clima de Medellín tiene temporadas de lluvia y temporadas secas que duran semanas; por eso la realidad recuerda más. Entonces, el mixing time de 2 días hay que leerlo como un mínimo: el clima real tarda un poco más en olvidarse. Si preguntan cómo mejorarlo: una cadena de segundo orden, en la que el estado sea la pareja (ayer, hoy), o estimar una matriz distinta para cada temporada. Esto muestra que no solo calculamos: interpretamos y cuestionamos el modelo con datos.

## 10. Demostración en vivo

Antes de exponer, abrir la app con uv run python -m streamlit run simulador/app.py y entrar a la página "Caso real: clima de Medellín" en el menú de la izquierda. Paso 1: mostrar la gráfica de lluvia, las tarjetas de arriba y las tablas de conteos y de P. Paso 2: cambiar "Lluvia fuerte desde" de 10 a 20 mm y mostrar que la matriz, π y el mixing time cambian; luego volver a 10. Paso 3: en la última sección, elegir "Lluvia fuerte" (la naranja queda arriba), "Seco" (la naranja queda abajo) y "Lluvia ligera" (casi coinciden). Cada sección tiene un recuadro "En palabras sencillas" para leer si hace falta.
