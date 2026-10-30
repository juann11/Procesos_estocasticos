# Simulador de cadenas de Markov

Trabajo Final de Procesos Estocásticos. Dada una matriz estocástica, determina si se alcanza un estado estable, calcula la distribución estacionaria y el mixing time, y compara la teoría con una simulación Monte Carlo.

## Cómo correrlo

Requiere [uv](https://docs.astral.sh/uv/).

```bash
uv run streamlit run app.py
```

## Pruebas

```bash
uv run pytest
```

## Archivos

- `markov.py`: lógica matemática.
- `app.py`: interfaz en Streamlit.
- `test_markov.py` y `test_app.py`: pruebas.
- `Reporte_especificacion.docx`: reporte de especificación.
