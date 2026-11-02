# F06 - TIGER/Line 2024, census tracts de Pensilvania
# El censo (F05) no trae mapa, entonces usamos el punto interno de cada tract
# para saber en que distrito queda. Guarda lago/tracts_distritos.csv
# Correr despues de f01

import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from ingesta.comun import asignar_distrito, descargar, guardar_csv

crudo = descargar(config.URL_F06, config.CRUDOS / "f06_tl_2024_42_tract.zip", "F06", timeout=900)
tracts = gpd.read_file(crudo)
tracts = tracts[tracts["COUNTYFP"] == "101"].copy()  # 101 = Filadelfia
print(f"  tracts de Filadelfia: {len(tracts)}")

# cada tract se asigna completo a un solo distrito (no se reparte si cruza el borde)
tracts["distrito_id"] = asignar_distrito(tracts, "INTPTLAT", "INTPTLON")
sin_distrito = tracts[tracts["distrito_id"].isna()]
if len(sin_distrito) > 0:
    print(f"  tracts sin distrito (normalmente son de agua): {list(sin_distrito.GEOID)}")
tracts = tracts[tracts["distrito_id"].notna()]

salida = tracts.rename(columns={"GEOID": "tract_geoid"})[["tract_geoid", "distrito_id"]]
guardar_csv(salida.sort_values("tract_geoid"), "tracts_distritos.csv")
