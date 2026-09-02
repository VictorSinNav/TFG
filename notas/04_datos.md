#### **04. Los datos**

Ya tenemos definido qué queremos predecir y con qué variables. Ahora toca conseguir los datos y dejarlos guardados de forma que todo lo que venga después pueda utilizarlos correctamente

Trabajamos con el **S&P 500** (ticker ^GSPC en Yahoo Finance), datos diarios desde el 1 de enero del 2000. Son unos datso de calidad para nuestro estudio ya que contienen varias características relevantes para el estudio: historia larga, incluye las crisis de 2008 y 2020, es el activo más estudiado en la literatura y los datos son gratuitos y razonablemente limpios.

La descarga se hace con la librería `yfinance`, que conviene aclarar que **no es una API oficial de Yahoo**, sino un cliente de terceros que consume sus endpoints públicos. Puede dejar de funcionar sin previo aviso, y esto condiciona parte de las decisiones que vienen a continuación.

Un detalle a tener en cuenta: el parámetro `start` es inclusivo y `end` es exclusivo. Por eso fijamos `end = 2026-09-01` para que el último dato sea el cierre del 31 de agosto de 2026.

#### **Por qué guardamos los datos en disco**

Los datos se descargan **una sola vez** y se guardan en `data/raw/` como CSV. Todo lo posterior lee de ese fichero y no vuelve a tocar la red. Hay tres razones:

1. **Reproducibilidad**: los proveedores revisan de vez en cuando sus series históricas. Con los datos congelados en disco, los resultados de la memoria se pueden reproducir aunque Yahoo cambie algo.
2. **Independencia del servicio**: si `yfinance` se rompe la semana de la defensa, el trabajo sigue funcionando.
3. **Coste**: el dataset se reconstruye decenas de veces mientras se ajustan ventanas y particiones. Leer un CSV local es inmediato.

Por el mismo motivo fijamos la fecha final de forma explícita en lugar de descargar "hasta hoy". Así dos ejecuciones separadas en el tiempo dan exactamente el mismo conjunto de datos. Además evitamos un problema sutil: si descargamos con el mercado abierto, la última fila corresponde a una sesión sin cerrar, y su "cierre" sería en realidad un precio intradía cualquiera.

#### **Precios ajustados**

Usamos `auto_adjust=True`, que corrige hacia atrás el efecto de dividendos y desdoblamientos:

- El día que se paga un **dividendo**, el precio cae mecánicamente por el importe repartido, aunque no ha habido ninguna pérdida real.
- Un **split** divide el precio sin que cambie el valor de la posición (una acción de 100 € pasa a ser dos de 50 €).

En una serie de acciones individuales, no corregir esto mete variaciones falsas que inflan la volatilidad estimada. En nuestro caso la distinción es irrelevante ya que la versión que descargamos se calcula sin dividendos, pero aún así vale la pena comentarlo.

#### **El formato de las columnas**

Comentar rápidamente que `yfinance`devuelve las columnas en dos niveles (multiindex). Hemos aplanado las columnas a un nivel antes de guardar


#### **Validaciones**

Sobre la tabla descargada comprobamos:

- Que estén las columnas `Open`, `High`, `Low`, `Close` y `Volume`.
- Que el índice sean fechas de verdad, crecientes y sin duplicados.
- Que no haya valores ausentes en `Close`.
- Que todos los precios sean positivos, condición necesaria para que exista el rendimiento logarítmico.
- Que el número de filas sea coherente con el rango pedido (unas 6.700 sesiones).

La idea aquí es observar cualquier posible anomalía, antes de volcar los datos y darse cuenta más tarde.

#### **Limitaciones**

- El proveedor no es una fuente institucional, así que no hay ninguna garantía sobre la calidad de la serie.
- Usamos precios de cierre diarios y no datos intradía, lo que condiciona el estimador de volatilidad tal como comentamos en la nota 02.