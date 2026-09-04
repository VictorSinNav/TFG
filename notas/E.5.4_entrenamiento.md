#### 5.4 ANFIS: el entrenamiento

**Qué se entrena y cómo**

Los 135 parámetros a la vez, por descenso de gradiente. Se propone (Jang, 1993) propone un aprendizaje híbrido (mínimos cuadrados para los consecuentes, gradiente para las premisas), pero nosotros usamos gradiente puro por dos razones: PyTorch lo hace en una línea, y ya partimos de la solución de HAR, que es precisamente lo que los mínimos cuadrados encontrarían en el primer paso.

Tasa de aprendizaje diferenciada. Los parámetros de premisa (a,b,c) y de consecuente (p,q) tienen sensibilidades muy distintas: mover un centro reorganiza qué reglas se activan, mientras que mover un coeficiente solo ajusta una recta. Usamos un paso 10 veces menor para las premisas, para que la estructura difusa no se desmonte en las primeras épocas.

Parada temprana sobre validación, igual que en el MLP.

Riesgo específico de ANFIS: que las anchuras se disparen. Si a -> $\infty$ todas las campanas se aplanan, todas las reglas valen lo mismo y ANFIS degenera en HAR. Lo vigilamos.