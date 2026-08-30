

#### **03. Las variables de entrada**

Antes de adentrarnos en los datos en si, deberíamos responder a una pregunta algo básica: **¿por qué creemos que la volatilidad futura tiene algo que ver con la pasada?** <br>

La respuesta es el agrupamiento de volatilidad observada por Mandelbrot en 1963. Los periodos agitados le suelen seguir periodos agitados, mientras que periodos tranquilos vienen seguidos de periodos también tranquilos.

Para cuantificarlo necesitamos un concepto: la **función de autocorrelación** (ACF). Esta función mide la correlación de la serie consigo misma desplazada *k* periodos: $$ \rho (k)= \frac{Cov(x_t, x_{t-k})}{Var(x_t)}, $$

siendo un valor cercano a 0 indica ausencia de relación lineal y cercano a 1 una relación positiva fuerte.

Lo que se observa empíricamente en cualquier serie financiera son dos hechos opuestos:

- $\rho (k)$ de los **rendimientos** $r_t \ \ \rightarrow $ prácticamente cero para todo $k \geq 1$
- $\rho (k)$ de los **rendimientos** $r_t^2 \ \ \rightarrow $ positiva y persistene durante decenas o cientos de días.


Esto es exactamente lo que dijimos anteriormente sobre el modelo $r_t = \sigma_t z_t$ : $ \mathbb{E}[z_t] = 0 $ anula la primera;  $ \mathbb{E}[z_t^2] = 1 $ deja intacta la segunda.


Además, tenemos el **problema de la larga memoria**, la cual da forma al modelo. Se tiene que la autocorrelación de $r_t^2$ no decae como cabría esperar.

- Un proceso autoregresivo clásico tiene **decrecimiento exponencial**: $\rho(k) \thicksim \Phi^k$, con $|\Phi| < 1$. A los 50 días ya es indistinguible de cero.
- La volatilidad decae de forma **hiperbólica**: $\rho(k) \thicksim k^{-\alpha}$ con $\alpha$ pequeño. A los 100 días sigue siendo apreciable.

Este fenómeno llamado memoria larga, rquiere procesos de integración fraccionaria para modelarlo con exactitud. Matemáticamente son elegantes pero son incómodos de trabajar (parámetros dificiles de estimar, sin interpretación evidente, implementaciones delicadas, ...)

#### **La solución de Corsi: la cascada de escalas**

Corsi (2009) parte de la siguiente hipótesis de que **el mercado es heterogéneo**: en el mercado no hay un único tipo de participante, sino varios con horizontes muy distintos. Operadores que reaccionan en minutos, gestores que revisan sus posiciones semanalmente, fondos institucionales que ajustan mensualmente, etc. La idea es que cad grupo genera volatilidad en su propia escala temporal, y las escalas se influyen entre sí en cascada.

Por lo tanto, en lugar de usar un modelo de memoria larga, usamos **una suma de tres componentes** con memorias cortas de distinta longitud:

$$RV_{t+1} = \beta_0 + \beta_1RV_t^{(1)} + \beta_2RV_t^{(5)} + \beta_3RV_t^{(22)} + e_t \ \ , $$

con,

- $RV_t^{(1)}$ componente diario 
- $RV_t^{(5)}$ componente semanal 
- $RV_t^{22)}$ componente mensual


El punto clave aquí, es que esta suma de tres términos reproduce empíricamente el decaimiento hiperbólico casi tan bien como un modelo de integración fraccionaria, con la ventaja obvia de ser una regresión lineal ordinaria que se estima por mínimos cuadrados.

Cabe recalcar que los tres números no son arbitrarios: 1 día, 5 días (una semana bursátil) y 22 días (un mes bursátil aproximadamente).

Así pues, para cada día $t$, el vector de entrada es: $$x_t = (RV_t^{(1)}, RV_t^{(5)}, RV_t^{(22)}) \in \mathbb{R}^3$$

en donde como fijamos anteriormente, $$RV_t^{(w)} = \sqrt{\frac{252}{w} \sum_{i=0}^{w-1}r_{t-i}^2}$$


Una pregunta que podría aparecer en este momento sería: ¿por qué utilizamos e variables en vez de 10?. El motivo principal es la maldición de la dimensionalidad, especialmente de los sistemas difusos. Hemos de pensar que un sistema difuso contiene una regla por cada combinacion posible. Con $n$ variables de entrada y $m$ conjuntos difusos por variable tenemos que: $$nº de reglas = m^n$$

Por ejemplo:
1. Para nuestro caso, **3 entradas** con por ejemplo **3 posibles conjuntos**, existen un total de 27 reglas.
2. Para un supuesto caso de **6 entradas** con el mismo número de conjuntos, obtenemos un total de 729 reglas
3. Aumenta exponencialmente: **10 entradas** con 3 conjnutos, se tiene un total de 59.049 reglas


En nuestro caso, con 27 reglas aún podremos inspeccionar e interpretar los resultados obtenidos. En cambio, con 729 reglas el modelo dejaría de ser entrenable. Es decir, la restricción viene de una propiedad estructural de los sistemas difusos.

Además de la maldición de la dimensionalidad, tener 3 entradas es positivo para poder comparar ANFIS con HAR, ya que tendran las mismas entradas, siendo así una comparación más limpia.


#### **Una cuarta variable**

Antes de proseguir debemos tener en cuenta el **efecto apalancamiento**. Dicho efecto describe la relación inversa y asimétrica entre los rendimientos de un activo y los cambios en su volatilidad:
- Rendimientos negativos provocan un aumento drástico e inmediato de la volatilidad.
- Rendimientos positivos tienden a mantener la volatilidad estable o incluso a diminuirla.


Como nuestras entradas son cuadrados, han perdido el signo y no pueden capturar estos cambios. La forma habitual de incorporarlo es añadir el rendimiento acumulado reciente, $ret_t^{(5)} = \sum_{i=0}^4 r_{t-1}$, que sí conserva el signo.

La decisión es que la calculamos pero no la usaremos al principio. Como hemos visto anteriormente pasaríamos a 81. Lo dejaremos como extensión para entrenar la variante de 4 entradas y comprobar si compensa el triple de reglas. 

Aún así creo que es interesante anotarlo, y si más no tener en cuenta las características y limitaciones de nuestro modelo.


