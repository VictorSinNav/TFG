"E0.0. Hago un planteamiento general de la parte práctica del trabajo"

"E0.1. Decido usar rendimientos logarítmicos debido a la aditividad temporal"

"E0.1_0.2. Volatilidad realizada anualizada a 5 días. Motivo: a 1 día el proxy tiene ~76% de error relativo (derivación vía $\chi_1^2$), lo que impediría distinguir entre modelos. Coste asumido: ventanas solapadas, errores autocorrelacionados."

"E0.3. Decido utilizar 3 variables de entrada. Me reservo una 4t variable en caso que sea necesario para combatir el efecto de apalancamiento"

"E0.4. Decido utilizar como fechas el intervalo 2000-01-01 / 2026-08-31 , rango el cual queda congelado para la realización del trabajo"

"E0.4. Reviso los datos descargados y parecen correctos y sin fallos (nº de filas correcto, rango correcto, no duplicados y no NaN)"

"E0.5 completado. Entrenamiento en escala logarítmica"

"E0.5 completado. Implementado splits.py . Partición cronologica. Embargo de 5 filas en las fronteras y normalización con los estadísticos de train. Creación de figura para la memoria" 

"E0.6. Exploración de los datos completada corroborando las decisiones teóricas previas"

"E.1. Creación del modelo ingenuo con ventanas de 1,5, y 22 días. Se decide que la mejor ventan es 5 días y que la métrica más relevante para evaluar el modelo es QLIKE"

"E.2. Creación del modelo HAR por MCO sobre las tres escalas logarítmicas, con transformación inversa a escala original para evaluar"

"E.2. Se pospone E2 (GARCH); HAR es el baseline prioritario por compartir entradas con ANFIS."

"E.2. Entradas sin normalizar: en una regresión lineal es indiferente y así los
  coeficientes son directamente legibles."