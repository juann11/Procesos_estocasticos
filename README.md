# Simulador de cadenas de Markov

Trabajo Final de Procesos Estocásticos. Dada una matriz estocástica, determina si se alcanza un estado estable, calcula la distribución estacionaria y el mixing time, y compara la teoría con una simulación Monte Carlo.

## Dónde está cada cosa

| Carpeta | Contenido |
|---|---|
| `simulador/app.py` | Interfaz web en Streamlit |
| `simulador/markov.py` | Lógica matemática |
| `pruebas/` | Pruebas automáticas |
| `documentos/` | Reporte, diapositivas en PDF, notas del orador y guía de exposición |

## Cómo correrlo

Requiere [uv](https://docs.astral.sh/uv/). Ejecuta los comandos desde la raíz del proyecto y abre `http://localhost:8501` en el navegador.

```bash
uv run streamlit run simulador/app.py
```

## Pruebas

```bash
uv run pytest
```

## Diapositivas

La versión editable está en https://claude.ai/artifact/JWjaZK4yd9mrsjsP6JzEm1 (privada hasta compartirla).
