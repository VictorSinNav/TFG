#### **5.1 ANFIS: Conjuntos difusos y funciones de pertenencia**

Llegamos al modelo central del trabajo y antes de montar la arquitectura conviene especificar las piezas clave de nuestro modelo

#### **Conjunto difuso**

Aunque en laparte de teoría se explica mejor conviene explicar brevemente que es un conjunto difuso para entender correctamente el código y sus resultados

En la teoría clásica de conjuntos, un elemento pertenece o no pertenece: la función indicadora de un conjunto $A$ solo toma los valores 0 y 1. Zadeh (1965) propone sustituirla por una función que puede tomar cualquier valor intermedio,

$$\mu_A : X \to [0,1],$$

llamada **función de pertenencia**. Decir que $\mu_A(x) = 0{,}7$ significa que $x$ pertenece a $A$ en grado 0,7.

La motivación es formalizar predicados vagos. La afirmación "la volatilidad es alta" no tiene una frontera nítida: nadie sostendría que 0,2999 es baja y 0,3001 es alta. Un conjunto difuso permite que la transición sea gradual.


#### **La campana generalizada**

Adoptamos la función de pertenencia que propone Jang (1993):

$$\mu(x; a, b, c) = \frac{1}{1 + \left|\dfrac{x - c}{a}\right|^{2b}}$$

Los tres parámetros tienen lectura geométrica inmediata. 
- El parámetro $c$ es el **centro**, el punto donde la pertenencia vale 1. 
- El parámetro $a$ es la **anchura**, en el sentido de que $\mu(c \pm a) = 1/2$.
- El paramétro $b$ controla la **pendiente de los flancos**: valores grandes producen una función casi rectangular, valores pequeños una transición muy suave.

Hay dos motivos para elegir esta forma:
1. El primero y decisivo es que es **derivable en todo punto**. Esta es una condición indispensable para poder utilizar el descenso por graidente. Una función triangular, aunque más simple, tiene picos donde la derivada no está definida. 
2. El segundo es que, frente a la gaussiana, el parámetro $b$ ofrece control independiente sobre la forma de las colas.

Sobre cada variable definimos tres conjuntos difusos, que interpretaremos como *baja*, *media* y *alta*. Con tres variables de entrada esto da $3^3 = 27$ reglas, el número que fijamos en la nota 03 por el argumento de la maldición de la dimensionalidad.


Necesitamos esta función ya que HAR aplica una única recta a todos los días, tranquilos o de pánico. ANFIS permite una recta distinta según el régimen, mediante reglas del tipo "SI $RV^{(1)}$ es *alta* Y $RV^{(5)}$ es *alta*, ENTONCES...". La función de pertenencia es lo que responde a "¿cuánto de *alta*?", y ese grado será el peso de la regla.



Si la partición fuera nítida (*alta* = por encima de 0,30), la predicción daría un salto brusco entre un día con 0,299 y otro con 0,301. Con grados de pertenencia ambas reglas están parcialmente activas cerca de la frontera y la transición es continua.


#### **La idea que convierte esto en una red neuronal**

El punto que hace de ANFIS algo más que un sistema difuso convencional es que los parámetros $a$, $b$ y $c$ **no se fijan a mano por un experto, sino que se aprenden de los datos**. Al declararlos como parámetros entrenables, el sistema difuso pasa a ser una red derivable y toda la maquinaria del descenso de gradiente se vuelve aplicable.

Este punto es exactamente el que buscamos en nuestro trabajo. La estructura de reglas aporta la interpretabilidad, y el aprendizaje automático aporta el ajuste a los datos.

#### **Un detalle de implementación**

El parámetro $b$ debe permanecer positivo, ya que un valor negativo invertiría la campana y la privaría de sentido. En lugar de recurrir a optimización con restricciones, se almacena su logaritmo y se recupera mediante $b = e^{\log b}$, que es positivo por construcción. Es una reparametrización habitual para imponer restricciones de positividad de forma transparente al optimizador.