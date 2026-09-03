# TFG - Aspectos matemáticos de las redes neuronales y su extensión a modelos difusos

Trabajo de Fin de Grado en Matemáticas.
Universidad Internacional de Valencia (VIU).

**Autor:** Víctor Sin Navarrete <br>
**Tutora:** Inma Garcés Andrés



## Descripción

Estudio de la fundamentación matemática de las redes neuronales artificiales
(teoremas de aproximación universal, aprendizaje como problema de optimización)
y de su extensión a sistemas neuro-difusos de tipo ANFIS, que combinan la
capacidad de aprendizaje de las redes con la interpretabilidad de las reglas
de la lógica difusa.

La validación empírica consiste en la predicción de la volatilidad diaria de
un índice bursátil, comparando el modelo neuro-difuso frente a modelos
econométricos clásicos (GARCH, HAR) y a una red neuronal estándar, con
análisis de interpretabilidad y de degradación en periodos de estrés.

## Estructura

- `data/` — datos brutos y procesados
- `notebooks/` — exploración y experimentos
- `src/` — código fuente del proyecto
- `results/` — figuras y tablas generadas
- `memoria/` — documento LaTeX

## Reproducibilidad

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Estado

En desarrollo.