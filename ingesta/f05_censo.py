# Censo población

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from ingesta.comun import descargar, guardar_csv

if not config.CENSUS_API_KEY and not (config.CRUDOS / "f05_acs.json").exists():
    raise SystemExit("Falta CENSUS_API_KEY en el archivo .env")

url = config.URL_F05 + "&key=" + config.CENSUS_API_KEY
crudo = descargar(url, config.CRUDOS / "f05_acs.json", "F05")

filas = json.loads(Path(crudo).read_text(encoding="utf-8"))
df = pd.DataFrame(filas[1:], columns=filas[0])
df["tract_geoid"] = df["state"] + df["county"] + df["tract"]

for col in ["B01003_001E", "B19013_001E"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df.loc[df[col] < 0, col] = None
print(f"  tracts: {len(df)}, sin ingreso: {df['B19013_001E'].isna().sum()}")

puente = pd.read_csv(config.LAGO / "tracts_distritos.csv", dtype=str)
df = df.merge(puente, on="tract_geoid", how="inner")

resultado = []
for distrito, g in df.groupby("distrito_id"):
    poblacion = g["B01003_001E"].sum()
    con_ingreso = g.dropna(subset=["B19013_001E"])
    peso = con_ingreso["B01003_001E"].sum()
    ingreso = (con_ingreso["B19013_001E"] * con_ingreso["B01003_001E"]).sum() / peso if peso > 0 else None
    resultado.append({"distrito_id": distrito,
                      "poblacion_total": int(poblacion),
                      "proxy_ingreso_mediano_hogar": round(ingreso, 2) if ingreso else None})

salida = pd.DataFrame(resultado)
print(f"  poblacion total: {salida.poblacion_total.sum()}")
guardar_csv(salida, "demografia_distritos.csv")