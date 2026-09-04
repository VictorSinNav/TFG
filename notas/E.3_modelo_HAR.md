#### **3. El modelo HAR**

El HAR (*Heterogeneous Autoregressive*) de Corsi (2009) es el modelo de referencia en la predicción de volatilidad realizada, y para este trabajo es la base más importante de todos.

$$\log \hat y_t = \beta_0 + \beta_1 \log RV_t^{(1)} + \beta_2 \log RV_t^{(5)} + \beta_3 \log RV_t^{(22)}$$

Cuatro parámetros, estimados por mínimos cuadrados ordinarios. Al ser un problema lineal, la solución tiene forma cerrada, $\hat\beta = (X^\top X)^{-1}X^\top y$, así que no hay optimización iterativa ni hiperparámetros que elegir. Esto tiene una consecuencia práctica y  es que el conjunto de validación no interviene en esta etapa.

#### **Por qué es el baseline que importa**

Como ya comentamos en la nota 03, las escalas de Corsi aproximan el decaimento hiperbólico de la autocorrelación sin tener que implementar la integración fraccionaria. Pero el motivo principa por el que HAR es de gran importancia es el siguiente.

Como se explico previamente **HAR es el caso particular de ANFIS con una sola regla.** Cuando el sistema difuso tiene $R=1$, el peso normalizado de esa única regla vale $\bar w_1(x)=1$ para todo $x$, y la salida se reduce exactamente a una función lineal de las entradas: precisamente esta regresión.

De ahí viene el argumento centra y más importante de este trabajo. HAR y ANFIS reciben **las mismas tres entradas**, así que cualquier diferencia de rendimiento entre ellos no puede atribuirse a la información disponible ni a la forma funcional local, que en ambos casos es lineal. Solo puede atribuirse a la **partición difusa** del espacio de entrada. La comparación aísla exactamente aquello que queremos medir.

#### **Escala y transformación inversa**

El modelo se ajusta sobre $\log y$ y devuelve logaritmos, así que las predicciones se transforman con la exponencial antes de calcular métricas, ya que estas se evalúan siempre en escala original.

Esto introduce el sesgo de Jensen: la exponencial de la media del logaritmo aproxima la mediana y no la media, de modo que las predicciones tienden a quedarse cortas. No obstante, como todos los modelos comparados sufren exactamente el mismo sesgo, el orden entre ellos no se ve afectado. Más que nada queríamos mencionarlo como una limitación, pero no corregiremos nada en nuestros cálculos

Un efecto colateral favorable del uso de logarítmos tal y como se mencionan en notas previas: la exponencial es siempre positiva, así que el modelo nunca puede predecir una volatilidad negativa. Un HAR ajustado directamente sobre $y$ sí podría hacerlo.

#### **Sobre los coeficientes y la inferencia**

Dos advertencias que conviene declarar antes de mirar la salida.

La primera es la **multicolinealidad**. Las tres entradas comparten rendimientos por construcción, con correlaciones superiores a 0,8. Esto no impide que la predicción conjunta sea válida, pero significa que los coeficientes individuales no admiten interpretación aislada. Es decir tener un $\beta_2 = 0,8$ y un $\beta_3 = 0,1$, no significa que la escala semanala tenga más impacto que la mensual. Podríamos repetir el modelo alterando los coeficientes y nos daría una predicción similar

La segunda es que **no realizamos inferencia estadística formal**. Como decidimos en la nota 02, el uso de ventanas solapadas hace que los residuos estén autocorrelacionados, de modo que los errores típicos que devuelve el ajuste están subestimados y los contrastes de significatividad no son fiables. Todas las conclusiones del trabajo se basan en comparación relativa entre modelos sobre el mismo conjunto de prueba.