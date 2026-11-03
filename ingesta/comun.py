# Funciones comunes para la ingesta de datos

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config

REGISTRO = config.EVIDENCIA / "registro_ingesta.json"


def ocultar_llave(url):
    return re.sub(r"(key=)[^&]+", r"\1***", url)


def anotar(entrada):
    registro = []
    if REGISTRO.exists():
        registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    registro.append(entrada)
    REGISTRO.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")


def usar_cache():
    return "--usar-cache" in sys.argv


def descargar(url, destino, fuente_id, timeout=300):
    # Descarga un archivo y guarda en evidencia la fecha, la respuesta y el sha256
    if usar_cache() and destino.exists():
        print(f"[{fuente_id}] usando archivo ya descargado: {destino.name}")
        return destino

    print(f"[{fuente_id}] descargando...")
    fecha = datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        r = requests.get(url, timeout=timeout, stream=True)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        h = hashlib.sha256()
        with open(destino, "wb") as f:
            for bloque in r.iter_content(1024 * 1024):
                f.write(bloque)
                h.update(bloque)
    except Exception as e:
        anotar({"fuente": fuente_id, "url": ocultar_llave(url), "fecha": fecha, "resultado": ocultar_llave(f"error: {e}")})
        raise RuntimeError(ocultar_llave(str(e))) from None

    anotar({"fuente": fuente_id, "url": ocultar_llave(url), "fecha": fecha, "resultado": "HTTP 200",
            "bytes": destino.stat().st_size, "sha256": h.hexdigest()})
    print(f"[{fuente_id}] listo ({destino.stat().st_size / 1e6:.1f} MB)")
    return destino


def guardar_csv(df, nombre):
    ruta = config.LAGO / nombre
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"  guardado lago/{nombre}: {len(df)} filas")
    return ruta


def leer_distritos():
    import geopandas as gpd
    ruta = config.LAGO / "territorio_distritos.geojson"
    if not ruta.exists():
        raise SystemExit("Primero hay que correr ingesta/f01_distritos.py")
    return gpd.read_file(ruta)


def asignar_distrito(df, col_lat, col_lon):
    import geopandas as gpd
    import pandas as pd

    lat = pd.to_numeric(df[col_lat], errors="coerce")
    lon = pd.to_numeric(df[col_lon], errors="coerce")
    puntos = gpd.GeoDataFrame(index=df.index, geometry=gpd.points_from_xy(lon, lat), crs=config.CRS_GEO)
    puntos = puntos[lat.notna() & lon.notna()]
    cruce = gpd.sjoin(puntos, leer_distritos()[["distrito_id", "geometry"]], how="left", predicate="within")
    cruce = cruce[~cruce.index.duplicated(keep="first")]  
    return cruce["distrito_id"].reindex(df.index)
