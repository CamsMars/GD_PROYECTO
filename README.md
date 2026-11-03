# Lago de datos vial de Filadelfia

Topicos de Sistemas de Informacion - EAFIT - Taller de datos

Integrantes: Camila Martinez, Miguel Gomez, Sebastian Castano y David Restrepo

## Estructura

```
config.py                  URLs, periodo (2020-2024) y categorias
ingesta/f01_distritos.py   F01 Planning Districts  -> lago/territorio_distritos.geojson
ingesta/f06_tracts.py      F06 TIGER tracts        -> lago/tracts_distritos.csv
ingesta/f05_censo.py       F05 ACS 2020-2024       -> lago/demografia_distritos.csv
ingesta/f02_311.py         F02 Philly311           -> lago/reportes_viales_311.csv
ingesta/f03_siniestros.py  F03 Crashes             -> lago/siniestralidad_vial.csv
ingesta/f04_septa.py       F04 SEPTA GTFS          -> lago/paraderos_septa.csv
construir_lago.py          indicadores por distrito y archivos de docs/datos/
verificar_privacidad.py    revisa que no se publiquen datos de personas
verificacion.sh            prueba las URLs con curl
armar_lago.py              corre todo en orden
docs/                      pagina web (index.html, app.js, estilos.css y datos/)
diccionario/               Excel del diccionario
evidencia/                 registro de descargas y verificaciones
```

La carpeta datos_crudos/ no se sube porque tiene coordenadas e IDs.

## Como correrlo

```
pip install -r requirements.txt
cp .env.ejemplo .env      (poner la llave del Census)
bash verificacion.sh
python armar_lago.py
```

Con `python armar_lago.py --usar-cache` no se vuelve a descargar lo que ya esta.

## Pagina web

La pagina esta en docs/ y se publica con GitHub Pages (Settings > Pages > Branch main, carpeta /docs).
Para verla en el computador: `cd docs` y `python -m http.server`, y abrir http://localhost:8000

Usa Leaflet y el mapa base de CARTO/OpenStreetMap, que no piden llave ni registro.

## Atribucion

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.
