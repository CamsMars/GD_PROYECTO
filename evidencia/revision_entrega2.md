# Estado de las correcciones de la segunda entrega

Revisión actualizada: 2026-11-03. Base previa de esta corrección: `1628270`.

## Estado actual

- La web de producción está en https://gd-proyecto-v6.vercel.app y se publica desde GitHub. Las notas antiguas que indicaban credenciales inválidas o publicación pendiente eran de una etapa anterior y ya no describen el estado actual.
- F05 conserva el endpoint de ingesta sin clave real en el catálogo, pero los enlaces visibles usan su ficha pública, accesible sin credenciales. El generador mantiene esta separación al reconstruir la web.
- README y web distinguen la cohorte de radicación de las fechas de cierre, y el periodo ACS de la instantánea SEPTA.
- La web publica agregados. El repositorio conserva también registros de detalle sin identificadores directos; ya no se presenta todo el repositorio como «solo agregados».
- El Excel mantiene seis fuentes integradas y 28 campos reales. Las otras fuentes y razones de descarte están en `fuentes_no_integradas.json`. No se cambiaron las fechas históricas de ingesta por hacer estas pruebas nuevas.

## Comparaciones nuevas ejecutadas

La evidencia está en `exploracion_2026-11-03/` y el procedimiento en `../exploracion/README.md`.

1. Requests y urllib: mismas siete URL, incluida la ficha pública y la API de F05. Se registraron muestras de hasta 4.096 bytes, estados, redirecciones, tipos y hashes. Para F02 se añadió `LIMIT 25` con los mismos filtros a ambos clientes; no se modificó la consulta anual de ingesta. La API sin clave muestra la limitación esperada; la ficha abre sin clave.
2. pandas y openpyxl: el mismo Excel produce seis fuentes y 28 campos, coincidentes con los archivos reales.
3. pandas y DuckDB: mismos CSV, conteos y 72 valores calculados (cuatro indicadores × 18 distritos), iguales al resultado publicado.
4. Python y JSON Schema: aceptan el GeoJSON real y rechazan ocho casos controlados en memoria, incluido un campo no publicable en el segundo distrito. No se alteraron archivos de producción para esas pruebas.
5. Streamlit y HTML/JS: mismos tres archivos agregados, ambos mapas con 18 polígonos, fuentes accesibles y vista móvil sin desbordamiento a 390 px. AppTest comprobó 108 combinaciones de indicador y distrito en Streamlit. Las capturas y el límite observado del clic del mapa están documentados en `comparacion_visualizacion.md`.

El primer intento se conservó en `intento_01.json` y `intento_01.txt`. El cliente DuckDB dejaba un resultado SQL sin consumir; se corrigió y se repitió. El acceso de muestra a F01 tuvo un fallo de conexión en ambos clientes; la nueva prueba terminó correctamente. No se conoce la causa de ese fallo ni se atribuye a la fuente un error de datos. `intento_03.json` y `intento_03.txt` conservan otra ejecución con HTTP 400 en la consulta anual de F02; al volver a consultar la misma URL respondió 200. La muestra final se acotó a 25 filas, de acuerdo con su alcance. En el intento inicial de F01 no hubo hash de contenido: su campo `prefijo_igual` no constituye evidencia de igualdad; el script final ya exige que exista un hash.

## Otros controles y resultados

- `verificar_entrega.py` y `verificar_privacidad.py` terminan correctamente; sus salidas reales están en `ejecucion.txt`.
- Cifras de control: 18 distritos, 408 tracts, 1.579.706 habitantes, 181.699 solicitudes, 36.303 siniestros y 7.987 paraderos.
- Registros sin distrito: 136 solicitudes y 451 siniestros, conservados en el lago y excluidos de los cálculos territoriales.
- La cohorte 311 tiene tres fechas locales 2019-12-31 por la conversión desde la selección UTC 2020–2024. El último cierre observado es 2026-10-29.
- Las pruebas previas de publicación dieron 404 para `.env`, `.git/config`, código Python y archivos crudos bajo el dominio de la web. Eso no implica que el repositorio público sea privado ni demuestra ausencia de todo riesgo de inferencia.

## Alcance que no se debe exagerar

Estas pruebas son nuevas y tienen versiones, hashes, resultados y capturas. No reemplazan el registro de ingesta original del 2026-11-02 ni demuestran una descarga integral nueva de las seis fuentes. Para esa descarga sigue haciendo falta una clave gratuita propia del Census. La prueba móvil es emulación de navegador; no se atribuye una prueba en un teléfono físico. Streamlit se ejecutó localmente y no se afirma un despliegue suyo en la nube.
