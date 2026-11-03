# Descarga distritos y calculo area en km2

import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from ingesta.comun import descargar

crudo = descargar(config.URL_F01, config.CRUDOS / "f01_planning_districts.geojson", "F01")
gdf = gpd.read_file(crudo).to_crs(config.CRS_GEO)
gdf.columns = [c if c == "geometry" else c.strip().lower() for c in gdf.columns]

gdf = gdf.rename(columns={"abbrev": "distrito_id", "dist_name": "nombre_distrito"})
gdf["distrito_id"] = gdf["distrito_id"].str.strip()
gdf["nombre_distrito"] = gdf["nombre_distrito"].str.strip()

if set(gdf["distrito_id"]) != set(config.DISTRITOS):
    raise SystemExit("Los distritos descargados no son los 18 esperados")

gdf["geometry"] = gdf.geometry.make_valid()

gdf["area_km2"] = (gdf.to_crs(config.CRS_AREA).area * config.PIES2_A_KM2).round(3)

salida = gdf[["distrito_id", "nombre_distrito", "area_km2", "geometry"]].sort_values("distrito_id")
salida.to_file(config.LAGO / "territorio_distritos.geojson", driver="GeoJSON")
print(f"  guardado lago/territorio_distritos.geojson: {len(salida)} distritos, {salida.area_km2.sum():.1f} km2")