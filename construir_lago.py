# Calcula los indicadores por distrito y genera los archivos de la pagina web
#   lago/indicadores_distrito.csv
#   docs/datos/distritos.geojson  (mapa con los indicadores)
#   docs/datos/preguntas.json     (resultados de P1, P2 y P3)
#   docs/datos/fuentes.json       (ID, licencia, periodo y fecha de prueba de cada fuente)

import json
from datetime import date

import geopandas as gpd
import pandas as pd
from scipy.stats import spearmanr

import config

LAGO = config.LAGO
WEB = config.WEB_DATOS

distritos = gpd.read_file(LAGO / "territorio_distritos.geojson")
reportes = pd.read_csv(LAGO / "reportes_viales_311.csv")
siniestros = pd.read_csv(LAGO / "siniestralidad_vial.csv")
paraderos = pd.read_csv(LAGO / "paraderos_septa.csv")
demografia = pd.read_csv(LAGO / "demografia_distritos.csv")

base = distritos[["distrito_id", "area_km2"]].merge(demografia, on="distrito_id", how="left")
poblacion = base.set_index("distrito_id")["poblacion_total"]
area = base.set_index("distrito_id")["area_km2"]

# Indicadores
n_reportes = reportes.groupby("distrito_id").size()
n_graves = siniestros.groupby("distrito_id")["siniestro_grave"].sum()
n_paraderos = paraderos.groupby("distrito_id").size()
cerradas = reportes[reportes["estado"] == "Closed"]

ind = pd.DataFrame(index=pd.Index(config.DISTRITOS, name="distrito_id"))
ind["reportes_viales_x1000hab"] = n_reportes / config.N_ANIOS / poblacion * 1000
ind["siniestros_graves_x1000hab"] = n_graves / config.N_ANIOS / poblacion * 1000
ind["paraderos_x_km2"] = n_paraderos.reindex(ind.index).fillna(0) / area
ind["mediana_dias_atencion"] = cerradas.groupby("distrito_id")["dias_atencion"].median()
ind = ind.round(3).reset_index()

ind.to_csv(LAGO / "indicadores_distrito.csv", index=False)
print("guardado lago/indicadores_distrito.csv")
print(ind.to_string(index=False))


# Preguntas
def correlacion(x, y):
    ok = x.notna() & y.notna()
    rho, p = spearmanr(x[ok], y[ok])
    if abs(rho) >= 0.6:
        fuerza = "fuerte"
    elif abs(rho) >= 0.4:
        fuerza = "moderada"
    else:
        fuerza = "débil o nula"
    sentido = "positiva" if rho > 0 else "negativa"
    return {"rho_spearman": round(float(rho), 3), "p_valor": round(float(p), 3),
            "n_distritos": int(ok.sum()), "lectura": f"relación {fuerza} {sentido}"}


t = ind.merge(demografia, on="distrito_id", how="left").set_index("distrito_id")
ranking = t["paraderos_x_km2"].sort_values(ascending=False)
nota = ("Con 18 distritos la relación describe zonas, no personas, y no prueba causa. "
        "La población y el ingreso son aproximaciones (PROXY).")

preguntas = {
    "periodo": f"{config.ANIO_INICIO}-{config.ANIO_FIN}",
    "generado": __import__("datetime").datetime.now(__import__("zoneinfo").ZoneInfo("America/Bogota")).date().isoformat(),
    "P1": {"pregunta": "¿Los distritos con más reportes viales al 311 por cada 1.000 habitantes "
                       "tienen también más siniestros graves por cada 1.000 habitantes?",
           "fuentes": ["F02", "F03", "F05", "F06", "F01"],
           **correlacion(t["reportes_viales_x1000hab"], t["siniestros_graves_x1000hab"]),
           "nota": nota},
    "P2": {"pregunta": "¿Qué distritos tienen más y menos paraderos de SEPTA por km²?",
           "fuentes": ["F04", "F01"],
           "mas": ranking.head(3).round(1).to_dict(),
           "menos": ranking.tail(3).round(1).to_dict()},
    "P3": {"pregunta": "¿Los distritos de menor ingreso tienen mayores tiempos de atención "
                       "a las solicitudes viales?",
           "fuentes": ["F02", "F05", "F06", "F01"],
           **correlacion(t["proxy_ingreso_mediano_hogar"], t["mediana_dias_atencion"]),
           "nota": nota + " Si la relación es negativa, a menor ingreso más días de atención."},
}

ultima_descarga = {}
registro = config.EVIDENCIA / "registro_ingesta.json"
if registro.exists():
    for r in json.loads(registro.read_text(encoding="utf-8")):
        if r.get("resultado") == "HTTP 200":
            ultima_descarga[r["fuente"]] = r["fecha"][:10]

catalogo = {}
excel = next(config.RAIZ.glob("diccionario/*.xlsx"), None)
if excel:
    hoja = pd.read_excel(excel, sheet_name="1. Fuentes", header=2, dtype=str)
    for _, f in hoja.iterrows():  # filas vacías se omiten por ID
        if isinstance(f.iloc[0], str) and f.iloc[0].startswith("F"):
            catalogo[f.iloc[0]] = {"nombre": f.iloc[1], "publica": f.iloc[2], "licencia": f.iloc[7],
                                   "periodo": f.iloc[10], "actualizacion": f.iloc[11], "url": f.iloc[4].split("&key=")[0]}

fuentes = {}
for fid in ["F01", "F02", "F03", "F04", "F05", "F06"]:
    fuentes[fid] = catalogo.get(fid, {})
    fuentes[fid]["fecha_prueba"] = ultima_descarga.get(fid, "sin registro")

# Archivos para la web
web = distritos.merge(demografia, on="distrito_id", how="left").merge(ind, on="distrito_id")
web["geometry"] = web.geometry.simplify(0.0002, preserve_topology=True)
web.to_file(WEB / "distritos.geojson", driver="GeoJSON", COORDINATE_PRECISION=5)
(WEB / "preguntas.json").write_text(json.dumps(preguntas, ensure_ascii=False, indent=2), encoding="utf-8")
(WEB / "fuentes.json").write_text(json.dumps(fuentes, ensure_ascii=False, indent=2), encoding="utf-8")

print("guardados docs/datos/distritos.geojson, preguntas.json y fuentes.json")
print(f"P1: {preguntas['P1']['lectura']} (rho = {preguntas['P1']['rho_spearman']})")
print(f"P3: {preguntas['P3']['lectura']} (rho = {preguntas['P3']['rho_spearman']})")