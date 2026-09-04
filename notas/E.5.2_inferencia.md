#### **5.2 ANFIS: la inferencia hacia delante**

Tenemos ya los grados de pertenencia. Falta ver cómo se combinan hasta producir un número. La arquitectura consta de cinco capas, y la primera es la que ya construimos.

#### **Capa 2: activación de las reglas**

Cada regla toma un conjunto difuso de cada variable, de modo que con tres conjuntos y tres variables resultan $3^3 = 27$ reglas, todas las combinaciones posibles. La regla $i$ tiene la forma

> SI $x_1$ es $A_{1,j_1}$ Y $x_2$ es $A_{2,j_2}$ Y $x_3$ es $A_{3,j_3}$, ENTONCES $\hat y = f_i(x)$

y su grado de activación es el producto de las tres pertenencias implicadas:

$$w_i(x) = \mu_{1,j_1}(x_1)\,\mu_{2,j_2}(x_2)\,\mu_{3,j_3}(x_3)$$

El producto implementa el "Y" de la regla. Con valores 0 o 1 el "Y" es evidente, pero aquí las pertenencias son intermedias y hay que decidir qué significa "0,8 Y 0,3". Las operaciones válidas para esto se llaman **t-normas**, y las dos habituales son el producto y el mínimo.

Usamos el producto por ser derivable en todo punto; el mínimo tiene una arista donde sus argumentos se cruzan, y todo el modelo se entrena por descenso de gradiente.

Además el producto es exigente: si una sola de las tres pertenencias es casi cero, la regla entera se apaga por muy altas que sean las otras dos. Justo lo que se espera de un "Y".



#### **Capa 3: normalización**

Las activaciones se normalizan dividiendo por su suma:

$$\bar w_i(x) = \frac{w_i(x)}{\sum_{k=1}^{27} w_k(x)}$$

Ahora sí suman uno. Esto tiene una consecuencia teórica muy útil que cabe remarcar: la salida pasa a ser una **combinación convexa** de las salidas locales, de modo que queda automáticamente acotada entre la menor y la mayor de ellas. El modelo no puede producir valores extremos por acumulación.

#### **Capa 4: los consecuentes**

Aquí hay que elegir entre las dos familias clásicas de sistemas difusos.

En un sistema de **Mamdani**, el consecuente de cada regla es a su vez un conjunto difuso: "ENTONCES la volatilidad es alta". El resultado de agregar todas las reglas es una función de pertenencia sobre la salida, que hay que convertir en un número mediante un procedimiento de *defuzzificación*, típicamente el centroide.

En un sistema de **Takagi-Sugeno-Kang**, el consecuente es una función nítida de las entradas. Adoptamos el caso de orden uno, en que esa función es afín:

$$f_i(x) = p_i^{(1)}x_1 + p_i^{(2)}x_2 + p_i^{(3)}x_3 + q_i$$

La razón de la elección es la misma de antes: TSK produce la salida directamente, sin ningún paso de defuzzificación, y la cadena completa resulta derivable. Es también la formulación sobre la que Jang define ANFIS en su artículo original.

Cada regla aporta cuatro parámetros, lo que da $27 \times 4 = 108$ parámetros de consecuente, que sumados a los $27$ de las premisas hacen un total de $135$.

#### **Capa 5: la salida**

$$\hat y(x) = \sum_{i=1}^{27} \bar w_i(x)\, f_i(x)$$

Merece la pena para un momento en la estructura de esta expresión. Cada $f_i$ es una función lineal, pero los pesos $\bar w_i$ dependen de $x$ de manera fuertemente no lineal, a través de las campanas de la capa 1. El modelo es por tanto **localmente lineal y globalmente no lineal**: en el entorno de cualquier punto se comporta aproximadamente como una recta, pero al desplazarse por el espacio de entrada esa recta va cambiando de forma continua.

Esta es exactamente la propiedad que buscábamos. La linealidad local es lo que hace legible cada regla por separado; la no linealidad global es lo que le da capacidad de ajuste.

#### **El caso de una sola regla**

Si el sistema tuviera una única regla, su peso normalizado valdría necesariamente $\bar w_1(x) = 1$ para todo $x$, y la salida se reduciría a

$$\hat y(x) = f_1(x) = p^{(1)}x_1 + p^{(2)}x_2 + p^{(3)}x_3 + q,$$

es decir, una regresión lineal sobre las mismas tres entradas. **ANFIS con una regla es exactamente el modelo HAR.**

Este resultado es el eje del trabajo, ya que como ambos modelos reciben las mismas variables y comparten la misma forma funcional local, cualquier diferencia de rendimiento entre ellos solo puede provenir de la partición difusa del espacio de entrada. La comparación aísla precisamente aquello que queremos medir, y conecta el capítulo teórico con el experimental sin necesidad de argumentos añadidos.