# Guion: caso real, el clima de Medellín

Presentación corta, solo del caso real (10 diapositivas, unos 10 minutos más la demo). Material:

- [`Caso_real_diapositivas.pptx`](Caso_real_diapositivas.pptx), con las notas del orador.
- La app, en la página **Caso real: clima de Medellín** del menú de la izquierda.

**JJ** = Juan José Ospina · **GG** = Geronimo Gaviria

---

### 1. Portada · JJ · 30 s

> Buenos días, profesora. Somos Juan José Ospina y Geronimo Gaviria. Todos hemos notado que en Medellín, cuando empieza a llover, suele seguir lloviendo unos días. Quisimos medir eso con lo que vimos en el curso: ¿cuántos días dura la memoria del clima?

### 2. La idea · JJ · 45 s

> El taller pedía un programa en el que el usuario escribe una matriz estocástica. Nosotros lo hicimos, pero quisimos ir más allá: en vez de inventar la matriz, la sacamos de datos reales. Así, los mismos cinco ítems del taller responden una pregunta de verdad: si hoy llovió, ¿cuántos días tarda ese dato en dejar de servir para predecir?

### 3. Los datos · JJ · 45 s

> Usamos la lluvia diaria de Medellín de 2023 a 2025: 1096 días, de la API de clima histórico de Open-Meteo. Cada día lo clasificamos en uno de tres estados: seco, si llovió menos de 1 milímetro; lluvia ligera, de 1 a 10, y lluvia fuerte, de 10 en adelante. Es como un calendario de tres años en el que pintamos cada día según cuánto llovió. Hubo 321 días secos, 518 de lluvia ligera y 257 de lluvia fuerte.

### 4. Ítem 1: la matriz se estima contando · JJ · 60 s

> Este es el paso clave. Recorrimos los días y anotamos, para cada uno, qué tipo de día vino después. Por ejemplo, de 257 aguaceros, 118 fueron seguidos por otro aguacero. Al dividir cada fila entre su total obtenemos probabilidades: 118 entre 257 da 0.459. Cada fila suma 1, así que es una matriz estocástica. Es decir: es una tabla de "qué suele venir después".

### 5. Ítem 2: la cadena sí se estabiliza · JJ · 45 s

> Le aplicamos el mismo criterio del simulador: hay estado estable si hay una sola clase cerrada y es aperiódica. Aquí desde cualquier tipo de día se puede llegar a cualquier otro, y cada día puede repetirse, así que no hay un ciclo obligado. Por eso el clima termina en un único reparto a largo plazo.
>
> Le paso la palabra a Geronimo.

### 6. Ítem 3: el clima a largo plazo · GG · 45 s

> Gracias. Resolviendo πP = π obtenemos que, a largo plazo, Medellín tiene 29 % de días secos, 47 % de lluvia ligera y 23 % de lluvia fuerte. Lo comparamos con lo que pasó de verdad en los tres años y es prácticamente igual. Es decir: π es el promedio a largo plazo. Si escogemos un día al azar, hay unas 29 de 100 posibilidades de que esté seco.

### 7. Ítem 4: el clima se olvida en 2 días · GG · 60 s

> Ahora la pregunta principal. Calculamos d(t), que mide qué tanto importa todavía cómo estuvo hoy. Al día siguiente vale 0.30, todavía por encima de ε = 0.25; al segundo día baja a 0.14. Entonces el mixing time es 2 días: después de eso, saber si hoy llovió casi no ayuda a predecir. Si somos más exigentes, con ε = 0.01 son 6 días.

### 8. La prueba: el modelo frente a la realidad · GG · 75 s

> Esto es lo que más nos gustó. No nos quedamos con el resultado: lo pusimos a prueba con la realidad. Buscamos todos los aguaceros y miramos qué pasó de verdad días después. Al día siguiente el modelo acierta exacto. Pero 5 días después de un aguacero, el modelo predice 24 % de lluvia fuerte y en la realidad fue 32 %. Y al revés: después de un día seco, en la realidad caen menos aguaceros de los que el modelo predice.

### 9. Lo que aprendimos · GG · 60 s

> El modelo acierta en lo importante: el reparto a largo plazo y el clima de mañana. Pero tiene un límite: solo mira el día anterior, y en Medellín hay temporadas de lluvia y temporadas secas que duran semanas. Por eso el clima real recuerda más. Entonces, los 2 días hay que leerlos como un mínimo. Para mejorarlo, se podría hacer una cadena que mire dos días atrás, o una matriz por temporada.

### 10. Demostración en vivo · JJ maneja, GG explica · 4 min

| Paso | Qué hacer | Qué decir |
|---|---|---|
| 1 | Abrir **Caso real: clima de Medellín** en el menú | "Aquí está todo calculado en vivo con los datos." |
| 2 | Mostrar la gráfica, las tarjetas y las tablas | "Estos son los conteos y la matriz que salió de ellos." |
| 3 | Cambiar **Lluvia fuerte desde** de 10 a 20 mm | "Si cambiamos qué cuenta como aguacero, todo se recalcula." Volver a 10. |
| 4 | En la última sección, elegir **Lluvia fuerte**, luego **Seco** | "Después de un aguacero la realidad queda arriba; después de un día seco, abajo." |
| 5 | Abrir un recuadro **"En resumen"** si hace falta | Leerlo si la profesora pide explicar algo. |

> **Ambos:** Muchas gracias. ¿Tienen alguna pregunta?

---

## Preguntas probables

**¿De dónde salen los datos?** De la API de clima histórico de Open-Meteo, lluvia diaria de Medellín de 2023 a 2025. Están guardados en `datos/clima_medellin.csv` y el script `datos/descargar_clima.py` los descarga de nuevo.

**¿Por qué 1 mm y 10 mm?** 1 mm es el umbral usual para decir que un día fue lluvioso, y 10 mm para lluvia fuerte. En la app se pueden cambiar.

**¿Por qué el modelo acierta exacto al día siguiente?** Porque la matriz se estimó justo con los pares (hoy, mañana). Por eso la prueba que importa es a 2 o más días.

**¿Por qué la realidad recuerda más?** Porque el clima tiene temporadas que duran semanas, y una cadena de Markov solo usa el día anterior. Esa memoria larga no la capta.

**¿Entonces el modelo está mal?** No: acierta el reparto a largo plazo y el día siguiente. Lo que muestra es su límite, y saberlo es parte del análisis.

**¿Cómo lo mejorarían?** Con una cadena de segundo orden, donde el estado sea la pareja (ayer, hoy), o estimando una matriz distinta para cada temporada.

**¿Qué es |λ₂| aquí?** Vale 0.468 y explica la velocidad con que d(t) baja: aproximadamente como 0.468 elevado a t.
