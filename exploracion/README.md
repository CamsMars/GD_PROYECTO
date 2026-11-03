# Pruebas comparadas con datos reales

Estas pruebas se añadieron para reevaluar las decisiones de la segunda entrega.
Son pruebas nuevas; no se atribuyen al desarrollo histórico del grupo.

## Repetir las pruebas

Desde la raíz del repositorio, con Python 3.12:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-exploracion.txt
python exploracion/comparar.py
```

En PowerShell, activar con `.\.venv\Scripts\Activate.ps1`.
Los resultados se guardan en `evidencia/exploracion_AAAA-MM-DD/` con versiones,
hashes de los archivos de entrada y de los scripts, resultados y salida de los
controles. La ejecución termina con error si una comprobación no coincide.
`--sin-red` omite los accesos externos y los registra como no ejecutados.

Se contrastan:

1. **Rastreo e ingesta HTTP:** Requests y urllib descargan el mismo prefijo de
   cada recurso (máximo 4096 bytes); se registra estado, tipo, redirección y hash.
   La consulta de muestra de F02 conserva sus filtros y añade `LIMIT 25`;
   no sustituye la consulta anual de la ingesta.
   El endpoint ACS sin clave debe mostrar su limitación; la ficha pública debe
   abrir sin clave. Esto no es una descarga completa del lago.
2. **Catálogo y contrato:** pandas y openpyxl leen el mismo Excel y contrastan
   sus seis fuentes y 28 campos con las tablas reales.
3. **Preparación y consulta del lago:** pandas y DuckDB leen los mismos CSV,
   cuentan filas y recalculan los cuatro indicadores para los 18 distritos.
4. **Verificación y protección:** un contrato explícito en Python y JSON Schema
   aceptan el GeoJSON real y rechazan ocho alteraciones controladas en memoria,
   incluido un campo no publicable añadido al segundo distrito.
5. **Vistas:** Streamlit ejecuta 108 combinaciones de distrito e indicador con
   AppTest. Esto comprueba valores y lógica, no el mapa renderizado. Las pruebas
   de navegador y sus capturas se conservan por separado.

## Abrir las dos vistas para compararlas

Terminal 1:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory docs
```

Terminal 2:

```bash
python -m streamlit run exploracion/vistas_streamlit.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Abrir `http://127.0.0.1:8765` y `http://127.0.0.1:8501`.
Las dos vistas leen exactamente `docs/datos/distritos.geojson`, `fuentes.json`
y `preguntas.json`; ninguna necesita la clave del Census para mostrar los datos.
El mapa de ambas usa Leaflet 1.9.4 y OpenStreetMap. Se compara el marco de
publicación y la interacción (Streamlit frente a HTML/JS), no dos motores de mapas.
Streamlit se prueba localmente; no se afirma que se haya desplegado en su nube.

## Licencias y referencias de las herramientas

| Herramienta | Licencia | Referencia |
|---|---|---|
| Python / urllib | PSF-2.0 | https://docs.python.org/3/license.html |
| Requests | Apache-2.0 | https://github.com/psf/requests/blob/main/LICENSE |
| pandas | BSD-3-Clause | https://github.com/pandas-dev/pandas/blob/main/LICENSE |
| openpyxl | MIT | https://pypi.org/project/openpyxl/ |
| DuckDB | MIT | https://github.com/duckdb/duckdb/blob/main/LICENSE |
| jsonschema | MIT | https://github.com/python-jsonschema/jsonschema/blob/main/COPYING |
| Streamlit | Apache-2.0 | https://github.com/streamlit/streamlit/blob/develop/LICENSE |
| Leaflet 1.9.4 | BSD-2-Clause | https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE |

API de pruebas: https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest.
Iframe: https://docs.streamlit.io/develop/api-reference/text/st.iframe.

No se publica la clave del Census, no se alteran las fechas de ingesta originales
y no se realiza una descarga integral nueva.
