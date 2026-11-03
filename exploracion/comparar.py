"""Comparaciones reproducibles sobre fuentes y archivos reales; no modifica el lago."""
import argparse
import copy
import csv
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

import duckdb
import jsonschema
import openpyxl
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
IDS = ['RW', 'NDEL', 'LFNE', 'CTR', 'USW', 'UNW', 'UNO', 'STH', 'NOR',
       'LS', 'LNE', 'CNE', 'WST', 'UFNE', 'LSW', 'WP', 'LNO', 'LNW']
RATE_FIELDS = ['reportes_viales_x1000hab', 'siniestros_graves_x1000hab',
               'paraderos_x_km2', 'mediana_dias_atencion']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equal(left, right, description):
    if left != right:
        raise AssertionError(f'{description}: las herramientas no coinciden')


def access_sources():
    """Leer el mismo prefijo (máximo 4096 bytes) con dos clientes HTTP."""
    catalog = json.loads((ROOT / 'docs/datos/fuentes.json').read_text())
    endpoints = []
    for fid, entry in catalog.items():
        url = entry['url']
        if fid == 'F02':
            parts = urlsplit(url)
            query = dict(parse_qsl(parts.query))
            query['q'] += ' LIMIT 25'
            url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
        endpoints.append((fid, url))
    endpoints.append(('F05_ficha_publica', catalog['F05']['url_publica']))
    results = []
    headers = {'User-Agent': 'GD-PROYECTO-Comparacion/1.0 (+https://github.com/CamsMars/GD_PROYECTO)',
               'Accept-Encoding': 'identity'}
    for fid, url in endpoints:
        clients = {}
        for client in ('requests', 'urllib'):
            try:
                if client == 'requests':
                    with requests.get(url, headers=headers, timeout=40, stream=True) as response:
                        parts, remaining = [], 4096
                        for block in response.iter_content(4096):
                            parts.append(block[:remaining])
                            remaining -= len(block[:remaining])
                            if remaining <= 0: break
                        body = b''.join(parts)
                        status, final, mime = response.status_code, response.url, response.headers.get('Content-Type', '')
                else:
                    with urlopen(Request(url, headers=headers), timeout=40) as response:
                        body = response.read(4096)
                        status, final, mime = response.status, response.url, response.headers.get('Content-Type', '')
                clients[client] = {'http': status, 'url_final': final, 'tipo': mime.split(';')[0],
                                   'bytes_muestra': len(body), 'sha256_muestra': hashlib.sha256(body).hexdigest(),
                                   'falta_clave': 'missing_key' in final or b'missing_key' in body}
            except Exception as error:
                clients[client] = {'error': type(error).__name__}
        expected = 'requiere_clave' if fid == 'F05' else 'accesible'
        valid = all(c.get('http') in (200, 206) and c.get('bytes_muestra', 0) > 0 for c in clients.values())
        if fid == 'F05':
            valid = valid and all(c.get('falta_clave') for c in clients.values())
        else:
            valid = valid and all(not c.get('falta_clave') for c in clients.values())
        results.append({'fuente': fid, 'url_probada': url, 'consulta_acotada_25_filas': fid == 'F02', 'resultado_esperado': expected, 'cumple': valid,
                        'prefijo_igual': bool(clients['requests'].get('sha256_muestra')) and clients['requests'].get('sha256_muestra') == clients['urllib'].get('sha256_muestra'),
                        'clientes': clients})
    if not all(r['cumple'] for r in results):
        # Conservar la evidencia incluso cuando haya una fuente caída.
        return {'cumple': False, 'alcance': 'muestras HTTP; no ingesta completa ni nueva fecha de prueba de los datos', 'fuentes': results}
    return {'cumple': True, 'alcance': 'muestras HTTP; no ingesta completa ni nueva fecha de prueba de los datos', 'fuentes': results}


def catalog_readers():
    path = ROOT / 'diccionario/Diccionario_datos.xlsx'
    # Un lector de tablas y otro del libro nativo, sobre el mismo archivo.
    frames = {name: pd.read_excel(path, sheet_name=name, header=2, dtype=str).fillna('')
              for name in ('1. Fuentes', '2. Diccionario')}
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    results = {}
    for tool in ('pandas', 'openpyxl'):
        sheets = {}
        for name in frames:
            if tool == 'pandas':
                rows = frames[name].values.tolist()
            else:
                rows = [[str(x) if x is not None else '' for x in row]
                        for row in list(book[name].values)[3:]]
            columns = (0, 1, 2, 4, 7, 10, 11, 12, 13) if name == '1. Fuentes' else (0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12)
            sheets[name] = [[row[c] for c in columns] for row in rows if row and row[0].startswith('F')]
        results[tool] = sheets
    equal(results['pandas'], results['openpyxl'], 'catálogo y diccionario')
    actual = set()
    for path in (ROOT / 'lago').glob('*.csv'):
        with path.open() as file:
            actual.update(('lago/' + path.name, field) for field in next(csv.reader(file)))
    geometry = json.loads((ROOT / 'lago/territorio_distritos.geojson').read_text())
    actual.update(('lago/territorio_distritos.geojson', field) for feature in geometry['features'] for field in feature['properties'])
    actual.add(('lago/territorio_distritos.geojson', 'geometry'))
    declared = {(row[1], row[2]) for row in results['pandas']['2. Diccionario']}
    equal(sorted(actual), sorted(declared), 'campos del contrato frente al lago')
    return {'cumple': True, 'lectores': ['pandas', 'openpyxl'], 'fuentes': len(results['pandas']['1. Fuentes']),
            'campos': len(declared), 'metadatos_iguales': True, 'campos_sin_documentar': 0,
            'sha256_libro': sha(ROOT / 'diccionario/Diccionario_datos.xlsx')}


def lake_queries():
    names = ['reportes_viales_311', 'siniestralidad_vial', 'paraderos_septa',
             'demografia_distritos', 'tracts_distritos', 'indicadores_distrito']
    frames = {n: pd.read_csv(ROOT / f'lago/{n}.csv') for n in names}
    db = duckdb.connect(':memory:')
    for name in names:
        db.read_csv(str(ROOT / f'lago/{name}.csv'), all_varchar=True).create_view(name)
    counts = {}
    for name in names:
        count = db.execute(f'SELECT COUNT(*) FROM {name}').fetchall()[0][0]
        equal(len(frames[name]), count, f'filas de {name}')
        counts[name] = count
    territory = json.loads((ROOT / 'lago/territorio_distritos.geojson').read_text())
    areas = pd.DataFrame([{'distrito_id': f['properties']['distrito_id'], 'area_km2': f['properties']['area_km2']}
                          for f in territory['features']])
    db.register('territorio', areas)
    reports, crashes = frames['reportes_viales_311'], frames['siniestralidad_vial']
    base = frames['demografia_distritos'].merge(areas, on='distrito_id').set_index('distrito_id')
    expected = pd.DataFrame(index=base.index)
    expected[RATE_FIELDS[0]] = reports.groupby('distrito_id').size() / 5 / base['poblacion_total'] * 1000
    expected[RATE_FIELDS[1]] = crashes.groupby('distrito_id')['siniestro_grave'].sum() / 5 / base['poblacion_total'] * 1000
    expected[RATE_FIELDS[2]] = frames['paraderos_septa'].groupby('distrito_id').size() / base['area_km2']
    expected[RATE_FIELDS[3]] = reports[reports['estado'] == 'Closed'].groupby('distrito_id')['dias_atencion'].median()
    sql = '''
      WITH reportes AS (SELECT distrito_id, COUNT(*) n FROM reportes_viales_311 GROUP BY distrito_id),
      graves AS (SELECT distrito_id, SUM(CAST(siniestro_grave AS DOUBLE)) n FROM siniestralidad_vial GROUP BY distrito_id),
      paraderos AS (SELECT distrito_id, COUNT(*) n FROM paraderos_septa GROUP BY distrito_id),
      cierres AS (SELECT distrito_id, MEDIAN(CAST(dias_atencion AS DOUBLE)) dias FROM reportes_viales_311 WHERE estado='Closed' GROUP BY distrito_id)
      SELECT d.distrito_id,
        reportes.n / 5.0 / CAST(d.poblacion_total AS DOUBLE) * 1000 AS reportes_viales_x1000hab,
        graves.n / 5.0 / CAST(d.poblacion_total AS DOUBLE) * 1000 AS siniestros_graves_x1000hab,
        paraderos.n / t.area_km2 AS paraderos_x_km2,
        cierres.dias AS mediana_dias_atencion
      FROM demografia_distritos d JOIN territorio t USING(distrito_id)
      LEFT JOIN reportes USING(distrito_id) LEFT JOIN graves USING(distrito_id)
      LEFT JOIN paraderos USING(distrito_id) LEFT JOIN cierres USING(distrito_id)
      ORDER BY d.distrito_id
    '''
    calculated = db.execute(sql).df().set_index('distrito_id').sort_index()
    expected = expected.sort_index()
    pd.testing.assert_frame_equal(expected, calculated, check_dtype=False, check_exact=False, atol=1e-9, rtol=1e-12)
    saved = frames['indicadores_distrito'].set_index('distrito_id').sort_index()[RATE_FIELDS]
    pd.testing.assert_frame_equal(expected.round(3), saved, check_dtype=False, check_exact=False, atol=1e-9, rtol=1e-12)
    values = expected.round(3).reset_index().to_dict(orient='records')
    absent = {n: int(frames[n]['distrito_id'].isna().sum()) for n in ('reportes_viales_311', 'siniestralidad_vial')}
    db.close()
    return {'cumple': True, 'herramientas': ['pandas', 'DuckDB'], 'filas': counts,
            'distritos': len(values), 'indicadores_comparados': len(RATE_FIELDS), 'valores_contrastados': len(values) * len(RATE_FIELDS),
            'sin_distrito': absent, 'coincide_con_publicado': True, 'resultado': values}


def validation_tools():
    data = json.loads((ROOT / 'docs/datos/distritos.geojson').read_text())
    fields = {'distrito_id': {'enum': IDS}, 'nombre_distrito': {'type': 'string', 'minLength': 1},
              'area_km2': {'type': 'number', 'exclusiveMinimum': 0},
              'poblacion_total': {'type': 'integer', 'minimum': 1},
              'proxy_ingreso_mediano_hogar': {'type': ['number', 'null'], 'minimum': 0}}
    fields.update({key: {'type': ['number', 'null'], 'minimum': 0} for key in RATE_FIELDS})
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object',
              'required': ['type', 'features'],
              'properties': {'type': {'const': 'FeatureCollection'}, 'name': {'type': 'string'},
                             'crs': {'type': 'object'}, 'xy_coordinate_resolution': {'type': 'number'},
                             'features': {'type': 'array', 'minItems': 18, 'maxItems': 18,
                               'items': {'type': 'object', 'required': ['type', 'properties', 'geometry'],
                                  'properties': {'type': {'const': 'Feature'}, 'properties': {'type': 'object', 'required': list(fields), 'properties': fields, 'additionalProperties': False},
                                      'geometry': {'type': 'object', 'required': ['type', 'coordinates'], 'properties': {'type': {'enum': ['Polygon', 'MultiPolygon']}, 'coordinates': {'type': 'array', 'minItems': 1}}}},
                                  'additionalProperties': False},
                               'allOf': [{'contains': {'properties': {'properties': {'properties': {'distrito_id': {'const': did}}}}}, 'minContains': 1, 'maxContains': 1} for did in IDS]}},
              'additionalProperties': False}
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)

    def python_valid(doc):
        try:
            if set(doc) - {'type', 'name', 'crs', 'xy_coordinate_resolution', 'features'}: return False
            if doc['type'] != 'FeatureCollection' or len(doc['features']) != 18: return False
            if {f['properties']['distrito_id'] for f in doc['features']} != set(IDS): return False
            for feature in doc['features']:
                if set(feature) != {'type', 'properties', 'geometry'} or feature['type'] != 'Feature': return False
                props = feature['properties']
                if set(props) != set(fields) or not isinstance(props['nombre_distrito'], str) or not props['nombre_distrito']: return False
                if type(props['poblacion_total']) is not int or props['poblacion_total'] < 1: return False
                for key in ['area_km2', 'proxy_ingreso_mediano_hogar'] + RATE_FIELDS:
                    value = props[key]
                    if value is None and key != 'area_km2': continue
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0: return False
                    if key == 'area_km2' and value == 0: return False
                if feature['geometry']['type'] not in ('Polygon', 'MultiPolygon') or not feature['geometry']['coordinates']: return False
            return True
        except (KeyError, TypeError):
            return False

    tests = [('archivo_real', copy.deepcopy(data), True)]
    def altered(name, change):
        value = copy.deepcopy(data)
        change(value)
        tests.append((name, value, False))
    altered('falta_un_distrito', lambda d: d['features'].pop())
    altered('id_desconocido', lambda d: d['features'][0]['properties'].update(distrito_id='ZZ'))
    altered('id_duplicado', lambda d: d['features'][0]['properties'].update(distrito_id=d['features'][1]['properties']['distrito_id']))
    altered('poblacion_negativa', lambda d: d['features'][0]['properties'].update(poblacion_total=-1))
    altered('poblacion_como_texto', lambda d: d['features'][0]['properties'].update(poblacion_total='83860'))
    altered('falta_indicador', lambda d: d['features'][0]['properties'].pop(RATE_FIELDS[0]))
    altered('campo_no_publicable_en_segundo_distrito', lambda d: d['features'][1]['properties'].update(address='DATO_FICTICIO_DE_PRUEBA'))
    altered('geometria_de_punto', lambda d: d['features'][0].update(geometry={'type': 'Point', 'coordinates': [0, 0]}))
    results = []
    for name, doc, expected in tests:
        a, b = python_valid(doc), validator.is_valid(doc)
        equal(a, expected, f'Python: {name}')
        equal(b, expected, f'JSON Schema: {name}')
        results.append({'caso': name, 'esperado': expected, 'python': a, 'jsonschema': b})
    return {'cumple': True, 'herramientas': ['Python (contrato explícito)', 'jsonschema Draft 2020-12'],
            'nota': 'Las modificaciones de prueba se hicieron en memoria, con datos ficticios; no se cambiaron los archivos publicados.', 'casos': results}, schema


def streamlit_checks():
    from streamlit.testing.v1 import AppTest
    settings = json.loads((ROOT / 'exploracion/indicadores.json').read_text())
    data = json.loads((ROOT / 'docs/datos/distritos.geojson').read_text())
    expected = {f['properties']['distrito_id']: f['properties'] for f in data['features']}
    app = AppTest.from_file(str(ROOT / 'exploracion/vistas_streamlit.py'), default_timeout=30).run()
    if app.exception: raise AssertionError('Streamlit no inició: ' + str(app.exception))
    checks = []
    for key in settings:
        for did in IDS:
            app.selectbox(key='indicador').set_value(key)
            app.selectbox(key='distrito').set_value(did)
            app.run()
            if app.exception: raise AssertionError(f'Streamlit falló en {key}/{did}')
            value = expected[did][key]
            formatted = format(value, f",.{settings[key]['decimales']}f") if value is not None else 'sin dato'
            equal(app.metric[0].value, formatted, f'Streamlit {key}/{did}')
            checks.append({'indicador': key, 'distrito': did, 'valor': value, 'mostrado': app.metric[0].value})
    return {'cumple': True, 'herramienta': 'Streamlit AppTest', 'distritos': len(IDS),
            'indicadores': len(settings), 'combinaciones_comprobadas': len(checks),
            'nota': 'AppTest verifica el backend y los valores. El renderizado real del mapa se prueba aparte en navegador.', 'comprobaciones': checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fecha', help='Fecha de la sesión de pruebas (AAAA-MM-DD); por defecto, America/Bogota.')
    parser.add_argument('--sin-red', action='store_true', help='Omitir la muestra HTTP, dejándola como no ejecutada.')
    args = parser.parse_args()
    date = args.fecha or datetime.now(ZoneInfo('America/Bogota')).date().isoformat()
    datetime.strptime(date, '%Y-%m-%d')
    output = ROOT / 'evidencia' / f'exploracion_{date}'
    output.mkdir(parents=True, exist_ok=True)
    inputs = list((ROOT / 'lago').glob('*.csv')) + list((ROOT / 'lago').glob('*.geojson')) + list((ROOT / 'docs/datos').glob('*')) + [ROOT / 'diccionario/Diccionario_datos.xlsx', ROOT / 'exploracion/indicadores.json']
    result = {'fecha_sesion': date, 'ejecutado_utc': datetime.now(timezone.utc).isoformat(),
              'base_git': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'sistema': platform.system(), 'arquitectura': platform.machine(), 'python': platform.python_version(),
              'versiones': {name: version(name) for name in ['pandas', 'openpyxl', 'requests', 'duckdb', 'jsonschema', 'streamlit', 'geopandas', 'shapely', 'scipy']},
              'sha256_entradas': {str(p.relative_to(ROOT)): sha(p) for p in sorted(inputs)},
              'sha256_scripts': {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'exploracion').glob('*.py'))},
              'alcance': 'Pruebas nuevas sobre las instantáneas existentes y muestras HTTP. No acreditan la descarga integral de las seis fuentes ni pruebas históricas anteriores.',
              'pruebas': {}}
    for key, call in [('catalogo', catalog_readers), ('lago', lake_queries), ('contrato_y_proteccion', validation_tools), ('streamlit', streamlit_checks)]:
        try:
            value = call()
            if key == 'contrato_y_proteccion':
                value, schema = value
                (output / 'contrato_web.schema.json').write_text(json.dumps(schema, ensure_ascii=False, indent=2) + '\n')
            result['pruebas'][key] = value
        except Exception as error:
            result['pruebas'][key] = {'cumple': False, 'error': str(error)}
        print(key, 'OK' if result['pruebas'][key].get('cumple') else 'ERROR', flush=True)
    if args.sin_red:
        result['pruebas']['acceso_http'] = {'ejecutado': False, 'motivo': '--sin-red'}
    else:
        result['pruebas']['acceso_http'] = access_sources()
        print('acceso_http', 'OK' if result['pruebas']['acceso_http'].get('cumple') else 'ERROR', flush=True)
    controls = []
    for name in ('verificar_entrega.py', 'verificar_privacidad.py'):
        check = subprocess.run([sys.executable, '-B', str(ROOT / name)], cwd=ROOT, text=True, capture_output=True)
        controls.append({'comando': f'python {name}', 'salida': check.stdout, 'error': check.stderr, 'codigo': check.returncode})
    result['controles_del_proyecto'] = controls
    (output / 'resultados.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    log = ['python exploracion/comparar.py --fecha ' + date + (' --sin-red' if args.sin_red else ''),
           'Python ' + platform.python_version(), json.dumps(result['versiones'], ensure_ascii=False)]
    log.extend(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in result['pruebas'].items() if key not in ('streamlit', 'lago'))
    log.extend(c['comando'] + '\n' + c['salida'] + c['error'] for c in controls)
    (output / 'ejecucion.txt').write_text('\n\n'.join(log) + '\n')
    failed = any(p.get('cumple') is False for p in result['pruebas'].values()) or any(c['codigo'] for c in controls)
    print('Evidencia:', output.relative_to(ROOT))
    if failed: raise SystemExit(1)


if __name__ == '__main__':
    main()
