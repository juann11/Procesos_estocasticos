# Notas del orador: Simulador de cadenas de Markov

## 1. Simulador de cadenas de Markov

Presentarnos: nombres y quién explica cada parte. Decir en una frase qué vamos a mostrar: un programa que recibe una matriz estocástica y dice si la cadena se estabiliza, a qué distribución llega y cuánto tarda.

## 2. Qué hace el programa

Los cinco pasos corresponden a los cinco ítems del enunciado, en el mismo orden. El quinto, en oscuro, es nuestra funcionalidad particular. La página funciona de arriba abajo: cada sección solo aparece si la anterior salió bien.

## 3. Cómo está construido

Elegimos Python porque NumPy resuelve el álgebra lineal y Streamlit nos da la interfaz sin construir un frontend. La decisión de diseño importante es la separación: markov.py no sabe que existe una página web. Por eso las pruebas pueden llamar directamente a cada función.

## 4. Dónde está cada ítem en el código

Esta diapositiva sirve de mapa. Si el profesor pregunta dónde se calcula algo, podemos abrir markov.py e ir directo a la función. grafo_dot genera el dibujo del grafo y app.py solo muestra los resultados.

## 5. Conceptos que usa el programa

Repaso rápido de los términos. Si el tiempo es corto, se puede pasar rápido por esta diapositiva, pero conviene dominar cada definición porque el criterio del ítem 2 se apoya en todas ellas.

## 6. Ítem 1: entrada de la matriz

Por qué aceptamos fracciones: 0.3333 tres veces suma 0.9999 y una matriz con tercios se rechazaría. Escribiendo 1/3 la fila suma 1. La tolerancia de la suma es 10 a la menos 9, solo para absorber el redondeo. Cada celda se lee como texto y se convierte con la clase Fraction de Python.

## 7. Ítem 2: cuándo hay estado estable

Pueden existir estados transitorios: la cadena los abandona con el tiempo, así que no impiden la convergencia. El programa acepta ese caso, que una matriz regular no cubriría. Por eso el criterio es más general que pedir que alguna potencia de P tenga todas sus entradas positivas. Ejemplo de oscilación: la matriz [[0, 1], [1, 0]] tiene período 2.

## 8. Ítem 2: cómo lo decide el programa

El grafo es una salida real del programa, con el ejemplo de dos estados absorbentes. Warshall calcula qué estados alcanzan a cuáles. Dos estados están en la misma clase si cada uno alcanza al otro. Para el período se recorre la clase con BFS y se saca el MCD de nivel(u) + 1 − nivel(v) en cada arista u → v. Ese valor equivale al MCD de las longitudes de los ciclos.

## 9. Ítem 2: el período con dos ejemplos

El segundo ejemplo muestra por qué no basta mirar la diagonal: no tiene autolazos y aun así es aperiódica, porque combina ciclos de longitud 2 y 3. Ambos casos están en las pruebas automáticas. Este caso se agregó porque el experimento de romper el código mostró que el período no estaba bien cubierto.

## 10. Ítem 3: distribución de estado estable

π es la distribución que no cambia al aplicar P. Las n ecuaciones de πP = π son dependientes, por eso se agrega la condición de que π sume 1. Queda un sistema de n + 1 ecuaciones con n incógnitas, y lo resuelve numpy.linalg.lstsq. Como ya sabemos por el ítem 2 que hay una sola clase cerrada aperiódica, la solución es única.

## 11. Ítem 4: cómo calculamos el mixing time

Aquí cada uno explica con sus propias palabras para qué sirve el mixing time, igual que en el apartado 1.1 del reporte. Procedimiento: empezamos con t = 0 y P a la 0 igual a la identidad, calculamos d(t), y si todavía no baja de ε multiplicamos por P y repetimos. d(t) nunca aumenta con t, por eso el primer t que cumple es el mínimo. Si no se alcanza en 100 000 pasos, el programa lo avisa en vez de inventar un número. Fuente: Levin, Peres y Wilmer, Markov Chains and Mixing Times.

## 12. Ítem 4: el algoritmo en código

Esto es el resumen de la función mixing_time de markov.py. Con 2 estados se hacen pocas multiplicaciones. Cada paso cuesta una multiplicación de matrices, así que el tiempo crece con el número de pasos y con n al cubo. Medimos unos 0.7 segundos para 100 000 pasos en una cadena de 2 estados y cerca de 1 segundo con 12 estados. El código real suma una tolerancia de 10 a la menos 12 al comparar con ε, para que el redondeo no agregue un paso de más.

## 13. Ítem 4: ejemplo resuelto a mano

Este ejemplo también está como prueba automática. A mano: el peor estado inicial es E2, y d(t) = (5/6) · 0.4 elevado a t. En t = 1 da 0.3333, que no alcanza. En t = 2 da 0.1333, que ya está por debajo de 0.25. La línea punteada de la gráfica es ε.

## 14. Ítem 4: el mismo ejemplo, paso a paso

π es (0.8333, 0.1667). En cada paso comparamos cada fila de la potencia de P con π y nos quedamos con el peor caso. En t = 1 el peor caso es 0.3333, mayor que 0.25, así que seguimos. En t = 2 es 0.1333, menor que 0.25, así que el mixing time es 2. Se usa el peor caso porque el mixing time no debe depender del estado inicial.

## 15. Ítem 4: qué explica la velocidad

λ₂ es el segundo mayor valor propio en módulo. d(t) decae aproximadamente como |λ₂| elevado a t, y por eso en el ejemplo anterior aparecía 0.4 a la t. Valores calculados por el programa con ε = 1/4. Si preguntan por el último caso: el valor propio 0.5 está repetido, y por eso d(t) tiene la forma (t + 1) / 2 a la t. Comprobado a mano: en t = 4 da 0.3125 y en t = 5 da 0.1875, así que el mixing time es 5.

## 16. Ítem 5: simulación Monte Carlo

Esta es nuestra funcionalidad particular. Cada caminante arranca en un estado y salta según las probabilidades de su fila. En cada paso contamos cuántos hay en cada estado y comparamos con π. Es una comprobación independiente porque no usa el sistema lineal. La curva simulada se estanca en un nivel de ruido: con más caminantes se acerca a la teórica. Mostrar esto en vivo moviendo el control de caminantes. La semilla es fija para que el resultado se pueda repetir.

## 17. Ítem 5: cómo salta cada caminante

Técnicamente se usa la fila acumulada: (0.9, 1.0). El código cuenta cuántos valores acumulados son menores o iguales que u, y ese conteo es el siguiente estado. Con NumPy esto se hace para todos los caminantes a la vez, sin un ciclo por caminante, y por eso 100 000 caminantes son manejables. En cada paso se cuenta cuántos caminantes hay en cada estado y se divide entre N. El tamaño de los tramos es proporcional a las probabilidades, salvo el segundo, que se dibujó un poco más ancho para que quepa el texto.

## 18. Ítem 5: el efecto de los caminantes

Con la cadena ya mezclada, la distancia teórica es casi cero, así que lo que queda es ruido del muestreo. Este ruido baja como 1 sobre raíz de N, y raíz de 10 es aproximadamente 3.16. Por eso multiplicar los caminantes por 10 reduce el ruido cerca de 3 veces: de 0.0560 a 0.0193, a 0.0061 y a 0.0016. Se puede mostrar en vivo moviendo el control de caminantes.

## 19. Cómo validamos el programa

Las pruebas se escribieron antes que la lógica. Para comprobar las pruebas introdujimos 19 errores a propósito, por ejemplo cambiar max por min en d(t). Se detectaron 16. Los 3 restantes son protecciones contra redondeo con probabilidad muy baja, difíciles de provocar. Este experimento destapó un hueco real en el cálculo del período, que corregimos con dos pruebas nuevas. Las dos cadenas a mano son la regular de 2 estados y la absorbente con transitorios.

## 20. Alcance y límites del programa

Conocer los límites demuestra que entendemos el programa. Si una cadena no mezcla en 100 000 pasos, el programa no inventa un número: avisa que no se alcanzó ε. Con 12 estados, 100 000 caminantes y 1000 pasos, la simulación tarda unos 8 segundos. El límite inferior de ε evita pedir distancias tan pequeñas que el redondeo del computador domine.

## 21. Demostración en vivo

Antes de exponer: abrir la app con uv run streamlit run simulador/app.py desde la carpeta del proyecto, y entrar a localhost:8501 en el navegador. El primer arranque del computador puede tardar más de 30 segundos. Para cambiar un valor, hacer doble clic en la casilla. En el caso 4, si la matriz tiene tercios, escribir 1/3 y no 0.3333. Si cambian el número de estados, se reinicia la tabla.

## 22. Conclusiones

Cerrar repasando que se cumplieron los cinco ítems. Preguntas probables: por qué se usa la distancia de variación total, por qué ε = 1/4, qué pasa con los estados transitorios, cómo se calcula el período, por qué mínimos cuadrados y qué diferencia hay entre la cadena periódica y la reducible. Ambos deben poder abrir markov.py y señalar analizar_cadena, _periodo y mixing_time.

## 23. Anexo: preguntas sobre el método

Anexo para responder preguntas. No se expone si no hace falta. Fuente de las propiedades de d(t) y ε: Levin, Peres y Wilmer, Markov Chains and Mixing Times, capítulo 4. La propiedad de ε = 1/4 dice que d(ℓ · t_mix) es menor o igual que 2 a la menos ℓ.

## 24. Anexo: preguntas sobre el programa

Anexo para responder preguntas sobre decisiones de programación. Si piden ver el código, abrir simulador/markov.py. También pueden pedir correr las pruebas: el comando es uv run pytest.
