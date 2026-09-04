#### **4. La red neuronal como estudio de ablación**

Es muy importanta antes de empezar el entrenamento del modelo de red neuronal,la finalidad más importante de esta etapa. Aquí no se busca el mejor predictor posible, sino su función es otra: permitir atribuir correctamente una eventual mejora de ANFIS.

Es decir, si ANFIS supera a HAR, caben dos explicaciones. 
1. Puede que la ventaja venga de que ANFIS es no lineal mientras HAR si que es lineal
2. O por el contrario puede que venga específicamente de la estructura de reglas difusas. 

Ambas hipótesis son compatibles con el mismo resultado, y sin un tercer modelo no hay forma de distinguirlas.

El perceptrón multicapa (MLP) ocupa exactamente esa posición intermedia:

| | ¿No lineal? | ¿Difuso? |
|---|---|---|
| HAR | No | No |
| MLP | Sí | No |
| ANFIS | Sí | Sí |

Con los tres, la lectura queda determinada. Si MLP y ANFIS baten a HAR por un margen parecido, la ventaja es de la no linealidad y la estructura difusa no aporta precisión, aunque siga aportando interpretabilidad. Si ANFIS bate también al MLP, la partición difusa aporta algo propio. Y si ninguno supera a HAR, la conclusión es que el problema es esencialmente lineal en estas variables, lo cual es un resultado igual de publicable.

#### **La arquitectura**

Veremos en la parte teórica con mas detenimiento las estructuras de las redes neuronales, no obstante hacemos una pequeña introducción del modelo que vamos a utilizar.

Una sola capa oculta con ocho neuronas y activación tangente hiperbólica: tres entradas, ocho unidades ocultas, una salida. En total unos cuarenta parámetros.

El tamaño es deliberadamente pequeño. Un ANFIS con tres conjuntos difusos por variable tiene veintisiete reglas, y para que la comparación sea justa ambos modelos deben tener capacidad de orden similar. Si la red tuviera cien neuronas y ganase, no sabríamos si es por su estructura o simplemente por ser mucho mayor.

La no linealidad la aporta la tangente hiperbólica situada entre las dos capas afines. Conviene subrayar por qué es imprescindible: la composición de dos aplicaciones afines es de nuevo una aplicación afín, de modo que sin ella la red no sería más que un HAR con pasos intermedios innecesarios. Se elige tanh en lugar de ReLU porque la superficie que hay que aprender es suave y con solo ocho unidades una ReLU produciría una función lineal a trozos con muy pocos tramos.

#### **El entrenamiento**

A diferencia de HAR, aquí no hay solución cerrada, sino que los pesos se ajustan minimizando el error cuadrático medio mediante descenso de gradiente, con el algoritmo Adam, que adapta el tamaño del paso durante el proceso.

El elemento importante es la **parada temprana**. Se evalúa el error sobre el conjunto de validación en cada época, se conserva el estado con menor error de validación y se detiene el entrenamiento si no mejora durante cien épocas consecutivas. Sin este mecanismo, la red seguiría reduciendo el error de entrenamiento memorizando el ruido de la muestra, lo cual es exactamente el problema de sobreajuste que el anteproyecto identificaba como una de las patologías a diagnosticar.

Esta es también la primera etapa en la que el conjunto de validación cumple su función. HAR no lo necesitaba porque los mínimos cuadrados no tienen nada que elegir. El conjunto de prueba, en cambio, sigue sin intervenir.

#### **La normalización**

Las entradas se usan estandarizadas, con la media y la desviación calculadas únicamente sobre el conjunto de entrenamiento, tal como se estableció en la nota 04. El motivo es que el descenso de gradiente converge con dificultad cuando las variables tienen escalas dispares: la superficie de error se vuelve muy alargada y el algoritmo oscila en lugar de descender.

Para HAR esto era indiferente, ya que una transformación lineal de las entradas solo reescala los coeficientes sin alterar las predicciones. Para un modelo entrenado iterativamente no lo es.

#### **La reproducibilidad**

La inicialización de los pesos es aleatoria, así que dos entrenamientos distintos dan resultados distintos. Se fija una semilla para que el experimento sea reproducible, y esto se declara en la memoria. Conviene recordar que un único entrenamiento no permite distinguir entre una mejora real y una inicialización afortunada.