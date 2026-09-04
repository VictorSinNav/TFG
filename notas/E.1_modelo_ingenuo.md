#### **1. El modelo ingenuo y las métricas**

Antes de construir nada complicado hace falta saber contra qué comparamos. Un RMSE de 0,05 no significa nada por sí solo: puede ser excelente o ridículo según lo que consiga un método trivial sobre los mismos datos.

#### **Los predictores**

Un modelo ingenuo predice la volatilidad futura copiando la pasada, sin ajustar ningún parámetro, es decir lo que viene es exactamente lo que acaba de pasar:

$$\hat y_t = RV_t^{(w)}, \qquad w \in \{1, 5, 22\}$$

El más interesante es el de cinco días, porque predice una ventana de cinco días usando la ventana de cinco días inmediatamente anterior: ambas magnitudes tienen la misma longitud y la comparación es limpia.

Como no hay nada que entrenar, se aplican directamente al conjunto de prueba. El objetivo de este modelo es fijar el suelo por debajo del cual ningún modelo sofisticado es defendible.

Conviene destacar que seguramente este modelo será mejor de lo que puede aprecer a pimera vista. Como vimos anteirormente, la volatilidad tiene una autocorrelación muy fuerta, así que si simplemente copiamos el pasado reciernte, ya obtendremos una predicción razonable. Es decir, mejorar el modelo ingenuo no es nada trivial y en la práctica no todos los modelos lo conseguiran.

#### **Las métricas**

Todas se calculan en escala original, nunca sobre logaritmos, porque hacerlo en escala logarítmica alteraría el orden de los modelos.

- **RMSE**, la raíz del error cuadrático medio. Se expresa en las mismas unidades que la volatilidad, pero al elevar al cuadrado queda dominado por unos pocos días extremos. Por esta razón no será la mejor métrica para medir nuestros resultados
- **MAE**, el error absoluto medio, más robusto frente a esos días.
- **QLIKE**, definida como

$$\text{QLIKE} = \frac{1}{n}\sum_i \left( \frac{y_i}{\hat y_i} - \log\frac{y_i}{\hat y_i} - 1 \right)$$

Esta última es la pérdida estándar en el ámbito de volatilidad y tiene dos propiedades que las otras no. Es **relativa** en lugar de absoluta, de modo que un error del 10% pesa igual en un periodo tranquilo que en uno turbulento. Y es **asimétrica**, penalizando más infraestimar la volatilidad que sobreestimarla, que en gestión de riesgo es precisamente el error caro. Se anula solo cuando la predicción coincide con el valor observado.

#### **Desglose por régimen**

Todas las métricas se calculan tres veces: sobre el conjunto de prueba completo, sobre el periodo tranquilo y sobre el subperiodo de estrés de 2020. Un modelo que gana de media pero se desmorona en marzo de 2020 no sirve para el propósito declarado, y una media global lo ocultaría.

#### **Lo que se observa**

La predicción ingenua reproduce la forma general de la serie pero va sistemáticamente **retrasada**: reacciona a los picos después de que hayan ocurrido, no antes. Corregir ese retraso es justamente lo que se les pide a los modelos con parámetros, y medir hasta qué punto lo consiguen es uno de los objetivos del trabajo.