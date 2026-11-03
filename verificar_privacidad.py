# Revisa que no haya información privada en los archivos que se publican en la web

import json
import sys

import pandas as pd

import config

PROHIBIDAS = [
    "lat", "lon", "lng", "latitude", "longitude", "dec_latitude", "dec_longitude",
    "stop_lat", "stop_lon", "intptlat", "intptlon",
    "address", "zipcode", "media_url", "status_notes", "service_notice", "subject",
    "service_request_id", "solicitud_id", "crn", "siniestro_id",
    "owner_1", "owner_2", "grantor", "grantee", "name",
]


def leer_columnas(ruta):
    if ruta.suffix == ".csv":
        df = pd.read_csv(ruta)
        return list(df.columns), len(df)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    features = datos.get("features", [])
    columnas = sorted({c for f in features for c in f.get("properties", {})})
    return columnas, len(features)


errores = []
archivos = list(config.LAGO.glob("*.csv")) + list(config.LAGO.glob("*.geojson")) + list(config.WEB_DATOS.glob("*.geojson"))

for ruta in archivos:
    columnas, filas = leer_columnas(ruta)
    nombre = ruta.relative_to(config.RAIZ)
    malas = [c for c in columnas if c.lower() in PROHIBIDAS]
    if malas:
        errores.append(f"{nombre} tiene columnas que no deben publicarse: {malas}")
    # la web solo puede tener datos agregados por distrito
    if ruta.parent == config.WEB_DATOS and filas > len(config.DISTRITOS):
        errores.append(f"{nombre} tiene {filas} filas, deberia tener solo los 18 distritos")
    print(f"  revisado {nombre} ({filas} filas)")

if errores:
    print("\nERROR de privacidad:")
    for e in errores:
        print(" -", e)
    sys.exit(1)

permitidos = {"distritos.geojson", "fuentes.json", "preguntas.json"}
extras = {p.name for p in config.WEB_DATOS.iterdir() if p.is_file()} - permitidos
if extras:
    sys.exit(f"ERROR: archivos web no previstos: {sorted(extras)}")
print("\nOK: no se encontraron columnas de la lista prohibida. La geometría territorial y los IDs de distrito, tract y paradero son públicos. Este control no garantiza anonimato.")
