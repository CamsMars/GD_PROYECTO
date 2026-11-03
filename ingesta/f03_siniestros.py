# F03 - Crashes Data (PennDOT)
# Siniestros 2020-2024 ubicados por distrito. Se quitan el crn y las coordenadas
# antes de guardar lago/siniestralidad_vial.csv

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from ingesta.comun import asignar_distrito, descargar, guardar_csv

crudo = descargar(config.URL_F03, config.CRUDOS / "f03_crashes.geojson", "F03", timeout=900)

# solo leemos las propiedades; las coordenadas estan en dec_latitude y dec_longitude
with open(crudo, encoding="utf-8") as f:
    df = pd.DataFrame([feat["properties"] for feat in json.load(f)["features"]])
df.columns = [c.lower() for c in df.columns]

total = len(df)
df = df.drop_duplicates(subset="crn")
print(f"  siniestros: {total}, duplicados quitados: {total - len(df)}")

# vienen como decimales, los pasamos a entero
df["anio_accidente"] = pd.to_numeric(df["crash_year"], errors="coerce").astype("Int64")
df = df[df["anio_accidente"].between(config.ANIO_INICIO, config.ANIO_FIN)]
df["fallecidos_conteo"] = pd.to_numeric(df["fatal_count"], errors="coerce").fillna(0).astype(int)
df["heridos_graves_conteo"] = pd.to_numeric(df["susp_serious_inj_count"], errors="coerce").fillna(0).astype(int)
df["siniestro_grave"] = pd.to_numeric(df["fatal_or_susp_serious_inj"], errors="coerce").fillna(0).astype(int)

df["distrito_id"] = asignar_distrito(df, "dec_latitude", "dec_longitude")
print(f"  sin ubicar: {df['distrito_id'].isna().sum()}")

salida = df[["anio_accidente", "fallecidos_conteo", "heridos_graves_conteo", "siniestro_grave", "distrito_id"]]
guardar_csv(salida, "siniestralidad_vial.csv")
