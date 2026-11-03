"""Controles locales sobre los datos conservados; no descarga ni modifica fuentes."""
import csv
import json
from pathlib import Path
import math
import statistics

ROOT = Path(__file__).resolve().parent
def csv_rows(name):
    with (ROOT / 'lago' / name).open() as f:
        return list(csv.DictReader(f))

def require(condition, message):
    if not condition:
        raise SystemExit('ERROR: ' + message)

districts=json.loads((ROOT/'docs/datos/distritos.geojson').read_text())['features']
ids={f['properties']['distrito_id'] for f in districts}
require(len(ids)==18 and len(districts)==18, '18 distritos únicos')
reports=csv_rows('reportes_viales_311.csv')
crashes=csv_rows('siniestralidad_vial.csv')
stops=csv_rows('paraderos_septa.csv')
demo=csv_rows('demografia_distritos.csv')
require(all('2019-12-31' <= x['fecha_reporte'] <= '2024-12-31' for x in reports),'fecha local de Philly311 fuera del rango de conversión UTC')
boundary=sum(x['fecha_reporte'] < '2020-01-01' for x in reports)
print(f'Nota temporal: {boundary} solicitudes seleccionadas desde 2020-01-01 UTC tienen fecha local 2019-12-31.')
require(all(2020 <= int(x['anio_accidente']) <= 2024 for x in crashes),'año de siniestro fuera de periodo')
require(len({x['paradero_id'] for x in stops})==len(stops),'paraderos duplicados')
for rows in (reports,crashes,stops,demo):
    require(all(not x['distrito_id'] or x['distrito_id'] in ids for x in rows),'distrito desconocido')
for f in districts:
    p=f['properties']; did=p['distrito_id']
    population=p['poblacion_total']
    n=sum(x['distrito_id']==did for x in reports)
    serious=sum(int(x['siniestro_grave']) for x in crashes if x['distrito_id']==did)
    count=sum(x['distrito_id']==did for x in stops)
    for field,expected in [('reportes_viales_x1000hab',n/5/population*1000),('siniestros_graves_x1000hab',serious/5/population*1000),('paraderos_x_km2',count/p['area_km2'])]:
        require(math.isclose(p[field],expected,abs_tol=.001),f'{did}: {field} no concuerda')
    closed=[float(x['dias_atencion']) for x in reports if x['distrito_id']==did and x['estado']=='Closed' and x['dias_atencion']]
    require(math.isclose(p['mediana_dias_atencion'],statistics.median(closed),abs_tol=.001),f'{did}: mediana')
sources=json.loads((ROOT/'docs/datos/fuentes.json').read_text())
require(set(sources)=={'F01','F02','F03','F04','F05','F06'},'seis fuentes integradas')
require(all(x.get('url','').startswith('https://') and x.get('fecha_prueba') for x in sources.values()),'URL o fecha faltante')
print(f'OK: 18 distritos; {sum(int(x["poblacion_total"]) for x in demo):,} habitantes; {len(reports):,} solicitudes; {len(crashes):,} siniestros; {len(stops):,} paraderos')
print('OK: periodos, claves, duplicados de paraderos y cuatro indicadores recalculados para los 18 distritos')
