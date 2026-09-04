#### **05. Construcción del dataset**

En este apartado detallamos los pasos que se utilizaran en la construcción del dataset. la idea es poder tenerlo como referencia para entender cada decisión tomada en el código. 


#### **Rendimiento logarítmico**

Tal y como se ha explicado en notas anteriores se ha decidido usar el rendimiento logarítmico:

$$r_t = log P_t - logP_{t-1}$$

En pandas el comando es `np.log(close)diff()`. La primera fila obviamente quedara como fila nula ya que no se tiene nu $P_{t-1}$. Se decide más abajo como gestionar estos casos


#### **Entradas: volatilidad pasada**


$$RV_t^{(w)} = \sqrt{\frac{252}{w}\sum_{i=0}^{w-1} r_{t-i}^2}$$

Este sumatorio incluye el día $t$. Esto es así ya que en el día $t$ ya conoces $r_t$ ya que el mercado ha cerrado. En pandas es `r2.rolling(w).sum()`. Rolling mira hacia atras nunca hacia delante


#### **Objetivo: volatilidad futura**

$$y_t = \sqrt{\frac{252}{5}\sum_{i=1}^{5} r_{t+i}^2}$$

Aquí en cambio el sumatoria empieza en i=1, es decir los días estrictamente posteriores. Como la función `rolling` solo mirar para atrás, entonces para calcular la ventana de 5 días que termina en $t+5$, la traemos a la fila $t$ usando `.shift(5)`


#### **Variable en reserva**

$ret_t^{(5)}= \sum_{i=0}^4r_{t-i}$

Conserva el signo (efecto apalancamiento). 


#### **Limpieza**

Destacamos que las primeras 21 filas contendran valores nulos, ya que la ventana de 22 días no estará completa. Además, las últimos 5 días también ya que no contienen la volatilidad futura. Las eliminamos con `dropna()`



#### **Decisión importante: Entrenar con $log \ RV$**


1. La distribución de la volatilidad es fuertemente asimétrica a la derecha, mientras que la de su logaritmo es aproximadamente normal. Esto mejora el condicionamiento del problema de optimización.
2. Al deshacer el logaritmo con la exponencial, la predicción es positiva por construcción. Sin esa transformación nada impide que un modelo lineal prediga una volatilidad negativa, que no tiene sentido.
3. Los picos de las crisis dejan de dominar el error cuadrático, de modo que el ajuste no se concentra en un puñado de días extremos.



#### **La escala: por qué el logaritmo**

Los modelos se entrenan sobre $\log RV$ en lugar de $RV$, por tres motivos de mucho peso:

1. La distribución de la volatilidad es fuertemente asimétrica a la derecha, mientras que la de su logaritmo es aproximadamente normal. Esto pasa porque la mayoría de las veces la volatilidad esta en niveles bajoss, pero explota en momentos de pánico y estres. Esto genera una distribución asimétrica con una cola larga a la derecha, y entonces el algoritmo de optimización, descenso de gradiente, se vuelve inestable. Con el logarítmo se transforma aproximadamente en una normal
2. Al deshacer el logaritmo con la exponencial, la predicción es positiva por construcción. Sin este detalle podriamos encontrarnos casos con volatilidad negativa,lo cual no tiene sentido en el mundo real
3. Los picos de las crisis dejan de dominar el error cuadrático, de modo que el ajuste no se concentra en un puñado de días extremos.


#### **Partición temporal**

El objetivo ahora es el de dividir el dataset en entrenamiento, validación y prueba. Esta partición no podemos realizarla al azar, sino que deberemos realizarla por fechas. Esto es indispensable hacerlo así, ya que la volatilidad de hoy, esta altamente correlacionada con la volatilidad de ayer y a la de mañana. Por ejemplo, si el modelo entrena con datos de 2022 para predecir lo ocurrido en 2010, le estaríamos permitiendo saber el futuro. Es decir, de hacerlo al azar, el modelo no aprendería las dinámicas subyacentes de la volatilidad, sino que simplemente memorizaría puntos vecinos. 


Dividimos el dataset de la siguiente manera:


| Conjunto | Periodo | Uso |
|---|---|---|
| Entrenamiento | 2000-01-01 a 2015-12-31 | Ajustar parámetros. Incluye la crisis de 2008 |
| Validación | 2016-01-01 a 2019-12-31 | Hiperparámetros y parada temprana |
| Prueba | 2020-01-01 en adelante | Evaluación final. Incluye el COVID |
| Estrés | 2020-02-15 a 2020-04-30 | Subperiodo aislado dentro de prueba |
 

#### **Puntos de fuga**

Una vez dividido el modelo, el objetivo es asegurarnos bien de que no tenemos datos repetidos en ambas particiones. Es decir, el objetivo $y-t$ mira 5 días hacia delante, por lo tanto la última fila de entrenamiento (2015-12-31), contendra rendimientos de enero de 2026, los cuales estan en validación. Esto se resolvera usando embargo (eliminando las últimas 5 filas de cada conjunto antes de la siguient paritción)


#### **Estandarización**

Procedemos a estandarizar nuestros datos para que el descenso del gradiente funcione correctamente. Para evitar filtrar información del futuro, hemos de estandarizar solamente con los datos del entrenamiento. Es el equivalente a cuando el modelo este funcionando en la vida real y no pueda ver una media del futuro. Tendrá que usar la media y la desviación históricas que aprendio durante el entrenamiento