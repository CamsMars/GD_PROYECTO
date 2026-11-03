#!/usr/bin/env bash
# Prueba con curl que cada fuente responda y guarda el resultado en
# evidencia/verificacion_FECHA.txt (esa es la fecha de prueba del Excel)
# Uso: bash verificacion.sh

cd "$(dirname "$0")"
mkdir -p evidencia
FALLOS=0
if [ -f .env ]; then
  set -a; . ./.env; set +a
fi
HOY=$(date +%F)
SALIDA="evidencia/verificacion_${HOY}.txt"
LLAVE="${CENSUS_API_KEY:-sin_llave}"

probar () {
  resp=$(curl -s -L -o /dev/null -m 60 -r 0-2047 -w '%{http_code} %{url_effective}' "$3")
  codigo=${resp%% *}
  if [[ "$1" =~ ^F0[1-6]$ && "$2" != "ACS sin llave" && "$codigo" != 200 && "$codigo" != 206 ]]; then
    FALLOS=$((FALLOS + 1))
  fi
  final=${resp#* }
  url=${3//$LLAVE/***}
  final=${final//$LLAVE/***}
  if [ "$final" != "$url" ]; then
    url="$url (redirige a $final)"
  fi
  echo -e "$1\t$2\tHTTP $codigo\t$url" | tee -a "$SALIDA"
}

echo "Verificacion de fuentes $(date '+%F %T')" | tee "$SALIDA"
probar F01 "Planning Districts" "https://hub.arcgis.com/api/v3/datasets/0960ea0f38f44146bb562f2b212075aa_0/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1"
probar F02 "Philly311" "https://phl.carto.com/api/v2/sql?format=csv&q=SELECT%20service_request_id%20FROM%20public_cases_fc%20LIMIT%201"
probar F03 "Crashes Data" "https://hub.arcgis.com/api/v3/datasets/21154a8f1894449f839d2288726e9837_0/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1"
probar F04 "SEPTA GTFS" "https://www3.septa.org/developer/gtfs_public.zip"
probar F05 "ACS sin llave" "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=tract:000100&in=state:42%20county:101"
if [ -n "${CENSUS_API_KEY:-}" ]; then
  probar F05 "ACS con llave" "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=tract:000100&in=state:42%20county:101&key=${CENSUS_API_KEY}"
fi
probar F06 "TIGER tracts" "https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_42_tract.zip"
echo "Guardado en $SALIDA"
exit "$((FALLOS > 0))"
