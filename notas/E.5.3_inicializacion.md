#### **5.3. ANFIS: la inicialización**

Esta etapa es breve pero decisiva. Un ANFIS mal inicializado sencillamente no converge, y es uno de los motivos por los que el modelo tiene fama de delicado.

#### **El problema de NO incializar**

Si todos los conjuntos difusos arrancan con el mismo centro y la misma anchura, las nueve campanas son idénticas y las veintisiete reglas resultan indistinguibles entre sí. Cada una recibe el mismo peso $1/27$ y el sistema no discrimina absolutamente nada.

Lo grave no es el punto de partida en sí, sino que se trata de un **punto simétrico**. Al ser todas las reglas iguales, todas reciben el mismo gradiente y se actualizan de forma idéntica, de modo que siguen siendo iguales después de cada paso. El descenso de gradiente no puede romper esa simetría por sí solo.

La solución es situar los conjuntos difusos donde efectivamente hay datos. Con tres conjuntos por variable tomamos los percentiles 10, 50 y 90 de esa variable en el conjunto de entrenamiento, y los usamos como centros de *baja*, *media* y *alta* respectivamente.

#### **Consecuentes inicializados con HAR**

Los parámetros de los consecuentes se inicializan con los coeficientes del modelo HAR ajustado sobre las mismas entradas, asignando a todas las reglas la misma función lineal.

Esta decisión tiene una lectura precisa. Como establecimos en la nota 12, ANFIS con una sola regla coincide exactamente con HAR. Si todas las reglas comparten la misma recta, la media ponderada de todas ellas devuelve esa recta con independencia de los pesos, así que el modelo inicializado de este modo reproduce exactamente las predicciones de HAR antes de entrenar.



