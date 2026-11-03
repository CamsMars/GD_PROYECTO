# SEPTA GTFS

import io
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
    df = pd.concat([leer_paraderos(z, "google_bus.zip", "bus"),
                    leer_paraderos(z, "google_rail.zip", "rail")], ignore_index=True)

df = df.drop_duplicates(subset="paradero_id")
df["distrito_id"] = asignar_distrito(df, "stop_lat", "stop_lon")
print(f"  paraderos fuera de Filadelfia: {df['distrito_id'].isna().sum()}")
df = df[df["distrito_id"].notna()]

guardar_csv(df[["paradero_id", "red", "distrito_id"]], "paraderos_septa.csv")