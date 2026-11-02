# F02 - Philly311
# Descarga las solicitudes viales de 2020 a 2024, las ubica en su distrito y
# quita el ID y las coordenadas antes de guardar lago/reportes_viales_311.csv

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from ingesta.comun import asignar_distrito, descargar, guardar_csv


def fecha_local(serie):
    # las fechas vienen en UTC; las pasamos a hora de Filadelfia
    fechas = pd.to_datetime(serie, utc=True, errors="coerce", format="ISO8601")
    return fechas.dt.tz_convert("America/New_York").dt.date


partes = []
for anio in range(config.ANIO_INICIO, config.ANIO_FIN + 1):
    # revisar que las categorias existan con ese nombre en cada anio
    cat = descargar(config.url_f02_categorias(anio), config.CRUDOS / f"f02_categorias_{anio}.csv", "F02")
    cat = pd.read_csv(cat)
    cat = cat[cat["service_name"].isin(config.CATEGORIAS_VIALES)]
    print(f"  {anio}: {dict(zip(cat.service_name, cat.n))}")

    crudo = descargar(config.url_f02(anio), config.CRUDOS / f"f02_311_{anio}.csv", "F02")
    partes.append(pd.read_csv(crudo, dtype={"service_request_id": "string"}))

df = pd.concat(partes, ignore_index=True)
df.columns = [c.strip().lower() for c in df.columns]

# el ID solo se usa para quitar duplicados
total = len(df)
df = df.drop_duplicates(subset="service_request_id")
print(f"  duplicados quitados: {total - len(df)}")

df["fecha_reporte"] = fecha_local(df["requested_datetime"])
df["fecha_cierre"] = fecha_local(df["closed_datetime"])
print(f"  fechas de reporte que no se pudieron leer: {df['fecha_reporte'].isna().sum()}")

# dias de atencion solo para cerradas; si el cierre es antes del reporte queda vacio
dias = (pd.to_datetime(df["fecha_cierre"]) - pd.to_datetime(df["fecha_reporte"])).dt.days
print(f"  solicitudes con cierre antes del reporte: {(dias < 0).sum()}")
df["dias_atencion"] = dias.where((dias >= 0) & (df["status"] == "Closed")).astype("Int64")

df["distrito_id"] = asignar_distrito(df, "lat", "lon")
print(f"  sin ubicar: {df['distrito_id'].isna().sum()} de {len(df)}")

df = df.rename(columns={"status": "estado", "service_name": "tipo_solicitud"})
salida = df[["fecha_reporte", "fecha_cierre", "estado", "tipo_solicitud", "distrito_id", "dias_atencion"]]
guardar_csv(salida, "reportes_viales_311.csv")
