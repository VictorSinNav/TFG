## Datos y entradas

#### **01. Rendimiento logarítmico**

Antes de empezar con la carga de datos es importante entender que queremos calcular y porque.

Primero de todo me gustaría aclarar porque no modelamos precios. Los precios **no son estacionarios**. Es fácilmente observable como los precios del SP500 han aumentado claramente en las últimas decadas, dando así una media no estacionaria. Casi toda la maquinaria estadística de series temporales asume estacionariedad, así que trabajar con precios en bruto rompe las hipótesis desde el primer paso. <br>

También tenemos que los precios no son comparables entre activos ni épocas. Una subida de 20 puntos significan cosas muy diferentes si el precio esta en 400 o 6.000. En cambio, los rendimientos si son comparables. <br>

Tenemos dos definciones de rendimiento:

1. Rendimiento simple: $$R_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{P_t}{P_{t-1}} - 1$$
2. Rendimiento logarítmico: $$r_t = log(\frac{P_t}{P_{t-1}}) = log P_t - log P_{t-1}$$

Siendo la relación entre ellos,

$$r_t = log(1 + R_t), \ \ \ \ \ R_t = e ^{r_t} - 1 $$

Elegiremos el rendimiento logarítmico debido a los sigueinte motivos.

- **Aditividad temporal:** Si cogemos el rendimiento simple, observamos que al cabo de $k$ días el rendimiento se obtiene multiplicando lo coeficientes diarios, $$\frac{P_{t + k}}{P_t} = \prod_{i = 1}^k \frac{P_{t+i}}{P_{t+i-1}}$$ 
mientras que si cogemos los rendimientos logarítmicos el producto se convierte en una suma de rendimientos, $$r_t^{(k)} = log\frac{P_{t+k}}{P_{t}} = \sum_{i = 1}^k r_{t+i} $$
Es decir, **el rendimiento de k días es la suma de los k rendimientos diarios**. Esta es la principal propiedad que justifica esta elección. Si tenemos que los $r_i$ son independientes y con varianza $\sigma^2$, entonces la varianza de una suma de variables independientes es la sumas de las varianzas: $$Var(\sum_{i = 1}^k r_i) = k\sigma^2 , $$lo que implica directamente que la volatilidad a $k$ días sea $\sqrt{k} \sigma$ <br>
Esta es la regla de la raíz cuadrada del tiempo, y es exactamente de donde sale el factor $\sqrt{252}$ que usaremos para anualizar (ya que 252 son los días que esta abierto al año el mercado bursátil).

- **Simetría:** Una subida y una bajada de la misma magnitud logarítmica tienen el mismo tamaño con signo opuesto, mientras que con rendimientos simples esto no es así. Ejemplo: 100 -> 150 -> 100 , sería una subida del 50\% con una posterior bajada del 33,3\%. No suman cero aunque hayas vuelto al punto de partida, mientras que con logaritmos tendríamos +0,4055 y -0,4055. Esto importa cuando modelas la distribución de los rendimientos, porque la distribución de los rendimientos simples está estructuralmente sesgada a la derecha.

- **Los precios se mantienen positivos:** de $r_t = log(\frac{P_t}{P_{t-1}})$ se sigue que $$P_t = P_{t-1}e^{r_t}, $$
y como $e^x > 0 \ \  \forall x \in \mathbb{R}$, el precio nunca puede volverse negativo, sea cual sea el valor de $r_t$. El rendimiento logarítmico vive en todo $\mathbb{R}$ sin restricciones. En cambio con rendimientos simple tendríamos que imponer a mano que $R_t \geq -1 $. Más que una comodidad, esto nos indica que si modelamos los rendimientos con una distribución normal, cuyo soporte es todo $\mathbb{R}$, con logarítmos el modelo es consistente y con rendimientos simples produciría precios negativos con probabilidad positiva.



Una limitación de usar el rendimiento logarítmico es que estos rendimientos no son aditivos entre activos. En nuestro caso es irrelevante ya que solamente trabajaremos con un índice ya calculado y no con una cartera propia. Aún así conviene mencionarlo como una limitación honesta del uso de rendimientos logarítmicos.


#### **02. La volatilidad realizada y el horizonte de predicción**

Empecemos este apartado recordando varias definiciones básicas:

- **Varianza** de una variable aleatoria **X**: el valor esperado del cuadrado de su desviación respecto a la media, $Var(X) = \mathbb{E}[(X- \mathbb{E}[X])^2]$. Mide la dispersión.
- **Desviación típica:** su raíz cuadrada, $\sigma = \sqrt{Var(X)}$. Tiene la ventaja de estar en las mismas unidades que $X$.
- **Volatilidad** es simplemente la desviación típica de los rendimiento

Y aquí esta el problema central de todo este campo. Tenemos que $\sigma$ es un parametro de la distribución que genera los rendimientos, no es un valor que podamos "leer" en nigún lado. Lo que podemos observar concretamente son los rendimientos de cada día, pero la volatilidad por el contrario es una variable latente, es decir, una magnitud que existe en el modelo pero no es directamente leible. Esto tiene una consecuencia que se arrastraremos durante todo el trabajo: no podemos comparar nuestras predicciones contra la verdad, porque la verdad no esta disponible; tan solo podremos compararlas con un estimador ruidosos de la verdad.


Por otro lado, cabe destacar también que si tenemos $w$ rendimientos, el estimador natural de la varianza es la varianza muestral: $$\hat{\sigma}^2 = \frac{1}{w-1} \sum_{i=1}^w(r_i-\bar{r})^2$$

Pero en finanzas se usa casi siempre una versión simplificada: $$\hat{\sigma}^2 = \frac{1}{w} \sum_{i=1}^w r_i^2$$

Se trabaja de esta manera ya que el rendimiento logarítmico medio diario de un índice rona los $3x10^{-4}$. Al elevarlo al cuadrado queda del orden de $10^{-7}$. Pero el termino $r_i^2$ típico es del orden de $10^{-4}$. Por lo tanto la media aporta alrededor de una milésima del total, es decir es despreciable. En cambio, **estimarla introduce ruido**, porque $\bar{r}$ es a su vez una estimación con error. Es decir, podemos verlo como un intercambio sesgo-varianza, no una simplificación por comodidad.


Otro aspecto importante a destacar sobre la volatilidad es que por convención se exresa en escala anual. Es decir los rendimientos son diarios, pero la volatilidad se expresa anualmente. Si los $r_i$ son independientes y con varianza $\sigma^2$, la varianza de la suma de $k$ de ellos es $k\sigma^2$, y por tanto la volatilidad a $k$ días es $\sqrt{k} \sigma$. Como tenemos que un año bursátil tiene aproximadamente 252 días de negociación, se multiplica la varianza diaria por $\sqrt{252}$. Nuestra definición quedaría tal que: $$RV_t^{(w)} = \sqrt{\frac{252}{w} \sum_{i=0}^{w-1}r_{t-i}^2}$$ 

Es decir un valor de 0,2 significa "20\% anual". Una advertencia importante sobre la hipóteis: los rendimientos tienen una correlación casi nula, pero sus cuadrados están fuertemente correlacionados, y esto es lo que se denomina con agrupamiento de volatilidad. Es decir, la anualización sigue siendo la convención universal, pero es una aproximación. Intuitivamente esto quiere decir que **el signdo del movimiento es impredecible; su magnitud no**. Es decir, que el mercado ayer se moviera un 3\% no nos dice si hoy subira o bajará, pero sí nos dice que probablemente hoy también se movera mucho.

Ahora nos adentramos en una importante decisión: **el horizonte de predicción**. 
El objetivo del modelo es la volatilidad realizada de los cinco días siguientes, y no la del día inmediatamente posterior. La razón es que la volatilidad es una variable latente que solo podemos medir a través de un estimador construido con los rendimientos observados, y ese estimador es tanto más ruidoso cuantas menos observaciones intervienen en él. En el caso extremos del horizonte de un día, caso el cual se apoya solamente en un único rendiemiento al cuadrado se observa que:

Si suponemos $r_t = \sigma_t z_t$ con $z_t \ \thicksim N(0,1)$, entonces por definición $\frac{r_t^2 }{\sigma_t^2}  \thicksim \chi_1^2$, distribución cuya varianza es 2 (es decir $2k$ con $k=1$) y media 1. De modo que el error relativo de la estimación de la varianza asciende al $\sqrt{2} \approx 141\%$ y, tras tomar la raíz cuadrada, en torno al 76\% sobre la volatilidad. Con un obketivo tan contaminado y ruidoso, todos los modelos exhibirian errores similares y las diferencias quedarían enmascaradas. Promediar sobre cinco días reduce el error relativo del estimador a aproximadamente un 32%, nivel que permite discriminar entre especificaciones alternativas. 

No obstante, esta elección no equivale, sin embargo a que horizontes más largos sean preferibles sin más. Es decir, si ampliamos la ventana reducimos el ruido de medición, pero construimos sobre ventanas solapadas. El número de observaciones efectivamente independientes es del orden de n/w , de modo que al alargar la ventana reducimos el tamaño real de la muestra, y sumado a que a medida que crece el horizonte, la volatilidad futura se aproxima progresivamente a la pasada y por tanto el problema de predicción se vuelve trivial.


