"""Descarga la lluvia diaria de Medellín (2023-2025) de la API de clima histórico de Open-Meteo.

Uso, desde la raíz del proyecto: uv run python datos/descargar_clima.py
Guarda datos/clima_medellin.csv para que la app funcione sin internet.
"""
import csv
import json
from pathlib import Path
from urllib.request import urlopen

URL = (
    "https://archive-api.open-meteo.com/v1/archive?latitude=6.2518&longitude=-75.5636"
    "&start_date=2023-01-01&end_date=2025-12-31&daily=precipitation_sum&timezone=America%2FBogota"
)

with urlopen(URL, timeout=60) as respuesta:
    diario = json.load(respuesta)["daily"]

destino = Path(__file__).parent / "clima_medellin.csv"
with destino.open("w", newline="", encoding="utf-8") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(["fecha", "lluvia_mm"])
    escritor.writerows(zip(diario["time"], diario["precipitation_sum"]))
print(f"{len(diario['time'])} días guardados en {destino}")
