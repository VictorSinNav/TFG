## Volatilidad

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



Una limitación de usar el rendimiento logarítmico es que estos rendimientos no son aditivos entre activos. En nuestro caso es irrelevante ya que solamente trabajaremos con un índice ya calculado y no con una cartera propia. Aún así conviene mencionarlo como una limitación honesta del uso de rendimientos logarítmicos