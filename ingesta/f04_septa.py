# SEPTA GTFS

import io
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from ingesta.comun import asignar_distrito, descargar, guardar_csv


def leer_paraderos(zip_principal, nombre, red):
    with zipfile.ZipFile(io.BytesIO(zip_principal.read(nombre))) as z:
        stops = pd.read_csv(z.open("stops.txt"), dtype=str, encoding="utf-8-sig")
    stops.columns = [c.strip() for c in stops.columns]
    
    if "location_type" in stops.columns:
        stops = stops[stops["location_type"].fillna("0").replace("", "0") == "0"]
    stops["paradero_id"] = red + "_" + stops["stop_id"].str.strip()
    stops["red"] = red
    return stops


crudo = descargar(config.URL_F04, config.CRUDOS / "f04_gtfs_public.zip", "F04")
with zipfile.ZipFile(crudo) as z:
    calendarios = {}
    for feed in ("google_bus.zip", "google_rail.zip"):
        with zipfile.ZipFile(io.BytesIO(z.read(feed))) as interior:
            calendario = {}
            for archivo, columnas in (("calendar.txt", ["start_date", "end_date"]),
                                      ("calendar_dates.txt", ["date"])):
                if archivo in interior.namelist():
                    tabla = pd.read_csv(interior.open(archivo), dtype=str)
                    for columna in columnas:
                        if columna in tabla and tabla[columna].notna().any():
                            valores = tabla[columna].dropna()
                            calendario[f"{archivo}:{columna}"] = {"min": valores.min(), "max": valores.max()}
            calendarios[feed] = calendario
    (config.EVIDENCIA / "septa_calendarios.json").write_text(
        json.dumps({"nota": "Rangos declarados en el feed descargado; no prueban cobertura histórica 2020–2024",
                    "feeds": calendarios}, ensure_ascii=False, indent=2), encoding="utf-8")
    df = pd.concat([leer_paraderos(z, "google_bus.zip", "bus"),
                    leer_paraderos(z, "google_rail.zip", "rail")], ignore_index=True)

df = df.drop_duplicates(subset="paradero_id")
df["distrito_id"] = asignar_distrito(df, "stop_lat", "stop_lon")
print(f"  paraderos fuera de Filadelfia: {df['distrito_id'].isna().sum()}")
df = df[df["distrito_id"].notna()]

guardar_csv(df[["paradero_id", "red", "distrito_id"]], "paraderos_septa.csv")
