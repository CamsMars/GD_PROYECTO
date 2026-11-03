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
    columnas = list(features[0]["properties"]) if features else []
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

print("\nOK: no hay coordenadas, direcciones, texto libre ni IDs en los archivos publicados")