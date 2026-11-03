# Filadelfia · sistema de información

**Grupo:** David Restrepo — Curaduría y modelado de datos · Camila Martínez — Ingeniería de datos y pipelines ETL · Miguel Gómez — Desarrollo de interfaz y frontend · Sebastián Castaño — Ciberseguridad y gobernanza de privacidad

**Repositorio:** https://github.com/CamsMars/GD_PROYECTO  
**Aplicación:** https://gd-proyecto-v6.vercel.app  
**Revisado:** 2026-11-03

## Para quién y qué pregunta

Este proyecto busca organizar información pública de la ciudad de Filadelfia para explorar algunas diferencias entre sus distritos de planificación. La idea no era solamente reunir datos de distintas fuentes, sino integrarlos de manera que permitieran hacer comparaciones y responder preguntas concretas sobre movilidad, accidentalidad y condiciones socioeconómicas.

- **Usuario:** personas interesadas en consultar y comparar información territorial de Filadelfia, especialmente sobre movilidad, seguridad vial y condiciones socioeconómicas.
- **Preguntas:**
  1. ¿Los distritos que tienen más reportes de problemas en las vías a través de Philly311 por habitante también presentan una mayor tasa de accidentes graves por habitante?
  2. ¿Qué distritos tienen la mayor y la menor densidad de paraderos de SEPTA por kilómetro cuadrado?
  3. ¿Los distritos con menores ingresos tienen mayores tiempos de respuesta a los reportes viales de Philly311?
- **Escala y comparación:** trabajamos con los 18 distritos de planificación de Filadelfia. Para hacer las comparaciones, agregamos la información de las fuentes a esta escala territorial. Algunas preguntas utilizan tasas por habitante y otras indicadores por kilómetro cuadrado o medidas de ingreso.
- **Lo que decidimos no mostrar, y por qué:** en la aplicación no mostramos coordenadas exactas, direcciones, descripciones de texto libre ni identificadores que pudieran permitir reconocer a una persona o una solicitud específica. El objetivo del sistema es comparar información territorial, por lo que no necesitamos exponer registros individuales. Tampoco presentamos las relaciones estadísticas como si demostraran una causa: los resultados permiten identificar patrones, pero no explicar por sí solos por qué ocurren.

## La réplica

Tomamos como referencia el proyecto de ejemplo y conservamos su idea principal: integrar fuentes distintas mediante una arquitectura por capas y organizar los resultados para que puedan consultarse desde una interfaz. Sin embargo, no todas las fuentes de Filadelfia estaban disponibles de la misma manera, así que tuvimos que adaptar los procesos de consulta y descarga.

Las capas son conceptuales: los originales se descargan en `datos_crudos/` (Bronze, excluida de Git); `lago/` conserva tablas limpias de detalle y tablas agregadas (Silver y Gold); `docs/datos/` contiene la instantánea agregada que publica la web. Los datos de detalle del lago público no conservan identificadores directos de personas, pero no deben confundirse con los agregados de la interfaz.

Algunas de las adaptaciones más importantes fueron:

- **Philly311 (F02):** utilizamos la API de Carto SQL para consultar las solicitudes de servicio.
- **SEPTA (F04):** trabajamos con archivos GTFS comprimidos, que contienen información relacionada con el sistema de transporte.
- **TIGER/Line (F06):** utilizamos los shapefiles de Pensilvania correspondientes a 2024 para trabajar con la información geográfica.
- **ACS (F05):** consultamos la API REST del U.S. Census Bureau para obtener información demográfica y socioeconómica del periodo 2020–2024. Esta consulta requiere una clave de acceso (`CENSUS_API_KEY`).

El proceso de integración también tuvo intentos que no terminaron en resultados utilizables. Por ejemplo, intentamos incorporar la fuente F12, relacionada con información escolar, pero los tiempos de espera del servidor se repitieron y no encontramos condiciones de licencia suficientemente claras para continuar. Por eso decidimos no incluirla en el lago de datos.

Las fuentes están documentadas en dos lugares: el catálogo de metadatos que genera `construir_lago.py`, ubicado en `docs/datos/fuentes.json`, y el archivo `diccionario/Diccionario_datos.xlsx`, específicamente en la hoja **1. Fuentes**, donde se encuentra el catálogo de las seis fuentes integradas; las candidatas y descartadas se conservan en `evidencia/fuentes_no_integradas.json`.

También encontramos información que habría sido útil para ampliar el análisis, pero que no pudimos integrar. Un ejemplo es el volumen de tráfico medido mediante vehículos-kilómetro recorridos (VMT). Sin esa información, las tasas de accidentes por habitante no permiten distinguir completamente entre el efecto de la población residente y la cantidad de vehículos que circulan por cada distrito.

## ¿Se puede usar?

La posibilidad de utilizar cada fuente depende de las condiciones establecidas por quien la publica. Por eso diferenciamos entre las fuentes que integramos y aquellas que revisamos, pero finalmente descartamos.

| Fuente | Licencia o condición | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 · Distritos de planificación | City of Philadelphia License | No aplica a los datos agregados publicados | Integrada | Uso sujeto a las condiciones de la ciudad |
| F02 · Philly311 | City of Philadelphia License | Solicitudes de servicio de la ciudadanía | Integrada | Se publican datos agregados y sin campos identificadores |
| F03 · Accidentes viales | City of Philadelphia License | Registros de siniestros | Integrada | Se utilizan para análisis territorial |
| F04 · SEPTA | SEPTA License Agreement | No aplica a los datos de paraderos publicados | Integrada | Uso sujeto al acuerdo de licencia de SEPTA |
| F05 · ACS | Dominio público federal de Estados Unidos (17 U.S.C. §105) | Información censal agregada | Integrada | Datos públicos del U.S. Census Bureau |
| F06 · TIGER/Line | Dominio público federal de Estados Unidos (17 U.S.C. §105) | No aplica a los datos geográficos publicados | Integrada | Datos geográficos públicos |
| F12 · Fuente escolar | Licencia no suficientemente clara | Información relacionada con instituciones educativas | Descartada | Problemas de disponibilidad y falta de claridad sobre las condiciones de uso |

La licencia de los datos no debe confundirse con la de las herramientas utilizadas para construir el sistema. Para la interfaz usamos HTML, JavaScript nativo y Leaflet.js, esta última bajo licencia BSD-2-Clause ([texto oficial de Leaflet 1.9.4](https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE)). Streamlit (Apache-2.0) se ejecutó como alternativa en una comparación nueva de cierre de la entrega, registrada el 2026-11-03. No se atribuye esta prueba a la fase histórica de desarrollo.

## Bitácora de exploración

Las siguientes pruebas nuevas se realizaron para reevaluar y ratificar las decisiones de la entrega. En cada par se usaron los mismos archivos o URL y los mismos criterios. No se les atribuye una fecha histórica anterior.

Comando reproducible: `python exploracion/comparar.py` después de instalar `requirements-exploracion.txt`. El registro del 2026-11-03 está en [resultados](evidencia/exploracion_2026-11-03/resultados.json), [salida](evidencia/exploracion_2026-11-03/ejecucion.txt) y [pruebas de navegador](evidencia/exploracion_2026-11-03/navegador.json). Los pasos completos y licencias están en [exploracion/README.md](exploracion/README.md).

| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto | Qué resolvió | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| Rastreo e ingesta HTTP de muestra | Requests | Las mismas siete URL y un límite de 4.096 bytes por respuesta | Apache-2.0 | Memoria local; solo estados, tipos y hashes en la evidencia | Sí: `python exploracion/comparar.py` | Ejecutada | Seis recursos y la ficha pública de F05 comprobados; identifica la redirección de la API sin clave | La muestra no reconstruye las seis fuentes completas | Sí; mantiene el cliente de ingesta ya usado por el proyecto |
| Rastreo e ingesta HTTP de muestra | urllib | Las mismas URL y el mismo límite | PSF-2.0 (Python) | Igual que Requests | Sí, en el mismo comando | Ejecutada | Confirma los accesos con la biblioteca estándar | La misma limitación de clave de F05; no se midió rendimiento sostenido | Alternativa válida; no se cambió el cliente del pipeline porque ambos resolvieron la prueba |
| Catálogo y contrato | pandas | El mismo Excel final | BSD-3-Clause | Archivo local | Sí, en el mismo comando | Ejecutada | Seis fuentes y 28 campos, coincidentes con openpyxl y el lago | El lector tabular no se usa para editar estilos del libro | Sí; alimenta el generador existente sin introducir otro lector en producción |
| Catálogo y contrato | openpyxl | El mismo Excel final | MIT | Archivo local | Sí, en el mismo comando | Ejecutada | Lectura independiente del catálogo y diccionario; mismo resultado | No se necesitó su capacidad de edición de Excel para generar la web | Se conserva para contraste; pandas sigue siendo el lector del pipeline |
| Preparación y consulta del lago | pandas | Los mismos seis CSV y áreas de F01 | BSD-3-Clause | Memoria local | Sí, en el mismo comando | Ejecutada | Recalcula cuatro indicadores por 18 distritos: 72 valores, iguales a SQL y al resultado publicado | Este ensayo no prueba la ingesta cruda ni el desempeño a gran escala | Sí; permite conservar la integración con GeoPandas y el código existente |
| Preparación y consulta del lago | DuckDB | Los mismos CSV y áreas | MIT | Base temporal en memoria, sin servidor | Sí, en el mismo comando | Ejecutada | Conteos, agrupaciones, medianas y tasas equivalentes mediante SQL | El primer ensayo dejó un resultado SQL sin consumir; se corrigió el uso del cliente y se repitió | Alternativa SQL válida; queda como verificación independiente, no reemplaza el pipeline |
| Verificación y protección del contrato web | Python, comprobaciones explícitas | El GeoJSON real y ocho alteraciones controladas en memoria | PSF-2.0 | Memoria local | Sí, en el mismo comando | Ejecutada | Acepta el archivo real y rechaza los ocho casos inválidos, incluido un campo no publicable en el segundo distrito | La validación no demuestra anonimato universal | Sí; los controles numéricos y de privacidad existentes siguen siendo los del pipeline |
| Verificación y protección del contrato web | jsonschema | Exactamente los mismos nueve casos | MIT | Memoria local | Sí, en el mismo comando | Ejecutada | Mismos nueve resultados mediante un contrato declarativo guardado como evidencia | No recalcula por sí solo los indicadores desde los CSV | Complemento experimental; no se presenta como sustituto de la verificación numérica |
| Vistas y publicación | HTML/JS + Leaflet | Los tres JSON/GeoJSON agregados de `docs/datos/` | Leaflet BSD-2-Clause | Archivos estáticos en GitHub y Vercel | Sí: servidor HTTP local; despliegue desde GitHub | Probada en navegador | 18 polígonos, selección de indicador, ficha por clic y F05 pública; ancho móvil de 390 px sin desbordamiento | La web estática necesita reconstruir sus archivos para actualizar los datos | Sí; se ratifica después de esta comparación: conserva el sitio ya publicado y la ficha conectada al mapa |
| Vistas y publicación | Streamlit 1.66.1 | Los mismos tres archivos agregados; servidor Python local | Apache-2.0; Leaflet BSD-2-Clause | Los mismos archivos locales; no se subieron a un servicio nuevo | Sí: `python -m streamlit run exploracion/vistas_streamlit.py` | Probada con AppTest y navegador | 108 combinaciones correctas; mapa de 18 polígonos, selector de distrito y F05 pública; 390 px sin desbordamiento | En este prototipo el clic del mapa abre un rótulo y no cambia la ficha Python; no se probó despliegue en su nube | No reemplaza la web; queda como alternativa real y reproducible |

La muestra HTTP de F02 mantiene sus filtros de año y categorías y añade `LIMIT 25`; el límite se aplica a ambos clientes y no altera la consulta de ingesta. Los conteos y 72 valores se contrastan con todos los registros del lago guardado.

El primer intento también se conserva: [resultado](evidencia/exploracion_2026-11-03/intento_01.json) y [salida](evidencia/exploracion_2026-11-03/intento_01.txt). Falló el uso inicial del cliente DuckDB por dejar un resultado sin consumir; la muestra de F01 también terminó en un error de conexión en ambos clientes. Se corrigió el consumo del resultado SQL y se repitió el acceso HTTP sin la cabecera Range, leyendo el prefijo del flujo. No se determinó la causa del fallo de conexión ni se afirma que retirar esa cabecera lo explique. La ejecución final quedó correcta. También se conserva [otro intento con HTTP 400 en F02](evidencia/exploracion_2026-11-03/intento_03.json); la misma consulta anual respondió 200 al volver a comprobarla. La comparación final de acceso usa la muestra acotada, no acredita la consulta anual completa. En el registro inicial de F01, `prefijo_igual` no permite concluir igualdad porque ambos clientes fallaron y no hubo hash; ese caso quedó corregido en el script final.

## Protección

**Nivel de la web:** solo agregados por distrito. **Alcance del repositorio público:** también contiene filas de solicitudes y siniestros sin identificadores directos. Esos registros no se describen como agregados ni como una garantía de anonimato.

Desde el inicio decidimos que la aplicación debía permitir consultar información territorial sin exponer registros que pudieran identificar directamente a una persona. Esto fue especialmente importante para los datos de Philly311, porque las solicitudes pueden contener información sobre lugares y situaciones particulares.

- **Qué protegemos, y de quién:** protegemos la información que podría facilitar la identificación de personas a partir de los registros originales. La aplicación está pensada para mostrar indicadores por distrito, no para consultar solicitudes individuales.
- **Controles ejecutados:** `verificar_privacidad.py` revisa seis CSV y dos GeoJSON; `verificar_entrega.py` contrasta claves, periodos e indicadores. La salida actual del control de privacidad dice: `OK: no se encontraron columnas de la lista prohibida`. Permite la geometría territorial y los IDs públicos de distritos, tracts y paraderos; su alcance no es demostrar anonimato universal. La salida completa está en la evidencia de exploración.
- **Revisión de secretos en el historial:** para volver a descargar F05, la clave `CENSUS_API_KEY` debe configurarse en un archivo local `.env`, que está incluido en `.gitignore`. Para que otra persona pueda configurar el proyecto se dejó `.env.ejemplo` como plantilla, sin incluir la clave real. También revisamos que la clave no quedara expuesta en los archivos publicados ni en el repositorio.

## Herramienta elegida para las vistas

- **Qué necesitábamos mostrar:** indicadores por distrito, comparaciones entre territorios y resultados de las tres preguntas del proyecto. La información debía poder consultarse de forma sencilla, sin que el usuario tuviera que conocer cómo se construyó el lago de datos.
- **Qué teníamos que proteger:** los archivos publicados no debían exponer los registros originales ni los campos que habíamos decidido excluir por privacidad.
- **Por qué esta herramienta cumple las dos cosas, y cuál descartamos por poco:** finalmente utilizamos HTML, JavaScript nativo y Leaflet.js para construir una aplicación estática. La desplegamos en Vercel y dejamos la interfaz separada de los procesos de ingesta y transformación. Esto nos permitió publicar las vistas sin mantener un servidor Python activo para atender las consultas de la aplicación.

La comparación real con Streamlit queda en [evidencia/comparacion_visualizacion.md](evidencia/comparacion_visualizacion.md), con prototipo, comandos, resultados y capturas. Ambas vistas leen los mismos tres archivos agregados y usan Leaflet/OpenStreetMap. Se compara el marco de publicación y su interacción, no dos motores cartográficos. Streamlit funcionó; se mantiene HTML/JS porque preserva la publicación estática y la ficha enlazada al clic del mapa. Esta es una decisión ratificada tras pruebas nuevas, no una reconstrucción de una prueba histórica sin evidencia.

## Nuestra posición

**Gestión y gobierno de datos**

Durante el proyecto entendimos que tener acceso a una fuente pública no significa que podamos utilizarla de cualquier manera. Cada fuente tiene condiciones, formatos y niveles de calidad diferentes. Por eso fue necesario revisar su procedencia, documentar las condiciones de uso y decidir cuáles podían incorporarse al sistema.

La arquitectura por capas también responde a esa necesidad. No queríamos mezclar los datos tal como llegan de las fuentes con los indicadores que finalmente mostramos. Separar la ingesta, la transformación y los resultados facilita revisar de dónde viene la información y cómo se obtuvo. Aun así, los resultados dependen de la calidad y disponibilidad de las fuentes originales.

En el análisis encontramos que la relación entre los reportes viales por habitante y los accidentes graves por habitante fue muy baja (Spearman ρ = -0.105; p = 0.677). Para la relación entre ingreso mediano y tiempos de respuesta de Philly311 obtuvimos ρ = 0.191 y p = 0.447. En ninguno de los dos casos encontramos evidencia estadística suficiente para afirmar que existe una asociación. Esto no demuestra que no haya ninguna relación; significa que, con los datos y el alcance de este análisis, no podemos sostener esa conclusión.

También encontramos diferencias importantes en la densidad de paraderos: Central (CTR) presentó el valor más alto, con 48.1 paraderos por km², mientras que Lower South (LS) tuvo el más bajo, con 2.5 paraderos por km².

Estos resultados deben leerse teniendo en cuenta que trabajamos con 18 distritos y que las tasas por habitante no reflejan necesariamente cuántos vehículos circulan por cada zona. Por ejemplo, Lower South tiene áreas industriales y portuarias, por lo que su población residente puede no representar toda la actividad que ocurre allí. Además, el ingreso mediano funciona como una aproximación de las condiciones económicas del distrito, no como una descripción de cada uno de sus habitantes.

**Ciberseguridad**

La seguridad no fue algo que agregáramos únicamente al final para cumplir con la entrega. Tuvo efecto en decisiones de diseño desde el momento en que seleccionamos qué información publicar. En lugar de exponer los registros originales, trabajamos con datos transformados y agregados, y desarrollamos un script para revisar que los archivos finales no conservaran determinados campos sensibles.

La verificación automática de campos permite revisar una parte de esas decisiones. También entendimos que una validación automática tiene un alcance específico: puede detectar la presencia de ciertos campos, pero no reemplaza una evaluación completa de los riesgos de inferencia. Por eso, la protección del sistema depende tanto de las verificaciones técnicas como de las decisiones sobre qué datos conservar y cuáles publicar.

## Bitácora de IA

Durante el desarrollo, las herramientas de IA se utilizaron como apoyo y no como sustituto de las decisiones del equipo. Los resultados debían contrastarse con las fuentes, el código y las pruebas del proyecto.

| Tramo | Herramienta | Qué le encargamos | Qué entregó | Qué le corregimos |
|---|---|---|---|---|
| Registro 1 del Excel | Gemini | Encontrar la API REST sin llave de la ciudad para acceder a solicitudes de atención ciudadana 311. | Recomendó la API Carto SQL de OpenDataPhilly (servicio correcto), pero con la tabla incidents_part1_part2, que es la de delitos y no la de Philly311. | Parcial. La IA acertó el servicio pero se equivocó en la tabla: el resultado parecía plausible y solo falló al probar la URL exacta («column requested_datetime does not exist»). La tabla correcta es public_cases_fc. Verificar cada URL, no solo el servicio. |
| Registro 2 del Excel | Gemini | Buscar un dataset abierto con identidades y condenas de conductores infractores viales. | Proporcionó la ruta de API api.phila.gov/v1/court/dui_drivers.json | Inventado. La IA inventa endpoints verosímiles justo en los temas donde los datos personales no se publican en bloque: hay que probar cada URL antes de creerla. |
| Registro 3 del Excel | Claude | Revisar el Excel fila por fila y verificar cada URL, licencia y nombre de campo contra los portales oficiales | Señaló que F02 consultaba la tabla de delitos en vez de public_cases_fc; que las URL /dataset/…/resource/… no existen en el OpenDataPhilly actual; licencias distintas a las publicadas (F03, F08, F04); campos de F01 y F03 con nombres inexistentes; que F07 trae nombres de propietarios y que la API del Census ahora pide llave | Parcial. Se confirmaron la tabla equivocada de F02, los campos reales de F01 y F03, la URL de SEPTA, los propietarios en F07, los 404 de las URL antiguas y que la API del Census exige llave. Pero la IA revisora también falló: dijo que la categoría de baches era «Pothole Repair» (en 2026 es «Street Defect») y cambió la URL de Indego, que sí funcionaba. Además, un enlace oficial (F12) no respondió desde nuestra red. Revisar a la IA con la misma disciplina que a la IA que busca. |
| Registro 4 del Excel | Gemini | Encontrar una fuente abierta con población e ingreso por zona para Filadelfia | Propuso la API del American Community Survey 5 años (edición 2022) con las variables B01003_001E (población) y B19013_001E (ingreso mediano del hogar) por census tract, como API sin llave. | Parcial. La fuente y las variables eran correctas, pero el acceso «sin llave» ya no es válido y la edición estaba desactualizada (existía la 2020-2024). Lo que la IA afirma sobre cómo se accede a una API puede caducar: hay que probarlo el día de la entrega. Además, la licencia CC0 que tomamos de los metadatos no era la correcta: el profesor señaló que es dominio público de EE. UU. Un metadato automático tampoco reemplaza leer los términos de la fuente. |
| Registro 5 del Excel | Claude | Escribir los scripts de ingesta F01-F06, la construcción de indicadores y la verificación de privacidad, aplicando las correcciones de la Entrega 1 | Entregó config.py, ingesta/f01…f06, construir_lago.py, verificar_privacidad.py, verificacion.sh y armar_lago.sh. Los probó solo con datos simulados porque desde su entorno no podía descargar las fuentes. | Parcial. El código funcionó con los datos reales, pero la IA solo lo había probado con datos simulados y la lista de categorías venía de la primera entrega sin revisar por año. Antes de confiar en un resultado hay que correrlo con los datos reales y comparar cifras de control con valores conocidos, como la población de la ciudad. |

Estos cinco registros proceden de la bitácora existente del Excel. Las pruebas de octubre son declaraciones del equipo: los archivos de evidencia citados allí no están en el repositorio actual. El registro de ingesta del 2 de noviembre sí conserva respuestas HTTP 200 y hashes para F01–F06.

| Corrección de esta entrega | Herramienta | Encargo | Resultado | Verificación |
|---|---|---|---|---|
| Revisión documental y técnica, 2026-11-02 | Codex | Aplicar correcciones con evidencia existente | Ajustes de README, Excel, periodos y controles | Alcance actualizado en `evidencia/revision_entrega2.md`; se distinguen los registros históricos de las pruebas nuevas |
| Comparación nueva y cierre documental, 2026-11-03 | Codex | Crear y ejecutar alternativas con datos reales, corregir F05 y la documentación | Clientes HTTP, lectura doble del Excel, consultas pandas/DuckDB, contrato Python/JSON Schema y prototipo Streamlit | 72 valores contrastados, nueve casos de contrato y 108 combinaciones de Streamlit; primer intento fallido conservado y corregido. El navegador confirmó mapas, fuentes y tamaños móviles |

---

## Ejecución local

Para ejecutar el proyecto en un entorno local:

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/CamsMars/GD_PROYECTO.git
   ```

2. Entrar a la carpeta del proyecto:

   ```bash
   cd GD_PROYECTO
   ```

3. Crear y activar un entorno virtual:

   ```bash
   python -m venv .venv
   ```

   En Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   En macOS/Linux: `source .venv/bin/activate`.

4. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Crear el archivo `.env` tomando como referencia `.env.ejemplo` y agregar la variable `CENSUS_API_KEY` con una clave válida del U.S. Census Bureau.

6. Ejecutar las verificaciones y construir el lago:

   ```bash
   bash verificacion.sh
   python armar_lago.py
   python verificar_entrega.py
   ```

   En Windows, el comando `bash` requiere Git Bash o WSL.

7. Para consultar la interfaz localmente, entrar a la carpeta `docs` y levantar un servidor HTTP:

   ```bash
   cd docs
   python -m http.server 8000
   ```

   Luego abrir `http://localhost:8000` en el navegador.

La aplicación publicada también se puede consultar en: https://gd-proyecto-v6.vercel.app.

## Periodos y reproducibilidad

F02 y F03 cubren 2020–2024; F05 es ACS 2020–2024. F04 es una instantánea del feed GTFS descargado el 2026-11-02, no una reconstrucción de paraderos de 2020–2024. Su calendario de vigencia no se conservó en la evidencia original. Una nueva descarga puede cambiar los conteos. Las fechas de prueba proceden de `evidencia/registro_ingesta.json`, y no de la fecha de reconstrucción.

El repositorio público contiene tablas con filas de solicitudes y siniestros sin identificadores directos; la web publica agregados por distrito. La eliminación de campos directos no garantiza anonimato. No deben describirse todas las tablas del repositorio como agregadas.

La selección de Philly311 se aplica a timestamps UTC de 2020–2024. Después se convierten las fechas a America/New_York: tres solicitudes quedan con fecha local 2019-12-31. Se conservan y se documentan, sin modificar artificialmente sus fechas. La cobertura no equivale exactamente a cinco años calendario locales.

En F05 el Excel copia literalmente el enlace declarado en el campo `license` del metadato oficial de la API. La explicación de dominio público federal se conserva por separado. No son una cita literal y una interpretación jurídica intercambiables.


## Fondo del mapa y tamaños de pantalla

La interfaz usa el mapa estándar de OpenStreetMap desde
`https://tile.openstreetmap.org/{z}/{x}/{y}.png`, sin clave de API.
La atribución de OpenStreetMap permanece visible en el mapa. El navegador conserva
su caché normal y la aplicación no ofrece descargas masivas ni mapas sin conexión.
Política del servicio: https://operations.osmfoundation.org/policies/tiles/.

El título se limita a 36 px en escritorio y 24 px en pantallas estrechas.
Las tarjetas y las tablas se contienen en el ancho de la página; las tablas
tienen desplazamiento horizontal propio cuando lo necesitan.

La versión se comprobó en navegador con anchos de 320, 390, 768 y 1440 px:
sin desbordamiento de la página, mapa base cargado y atribuido, 18 distritos,
selector de indicadores, ficha de distrito y apertura/cierre de Fuente operativos.
La prueba de ancho móvil es una emulación de navegador, no una prueba en un teléfono físico.


## Calidad, fechas y límites de esta validación

| Fuente | Filas conservadas | Sin distrito | Filas usadas en los cálculos por distrito |
|---|---:|---:|---:|
| F02 · solicitudes | 181.699 | 136 | 181.563 |
| F03 · siniestros | 36.303 | 451 | 35.852 |

Las filas sin distrito se conservan en las tablas del lago, pero no se asignan artificialmente y no entran en los numeradores territoriales. El conteo total del lago y la suma de los conteos por distrito no son la misma población de registros.

La cohorte de solicitudes se selecciona por radicación UTC en 2020–2024. Sus cierres pueden ser posteriores: el máximo observado en la instantánea es 2026-10-29. Los siniestros se seleccionan por año de ocurrencia en 2020–2024. SEPTA es el feed descargado el 2026-11-02. Por tanto, no se afirma que todo dato de 2025 o 2026 quede fuera.

F05 conserva su endpoint de ingesta en el Excel y el metadato `url`; la interfaz utiliza `url_publica`, que abre [la ficha de ACS](https://api.census.gov/data/2024/acs/acs5.html) sin clave. La clave gratuita solo es necesaria para volver a descargar los datos del Census y nunca se publica.

Las fechas de descarga de F01–F06 siguen siendo las del registro original de ingesta del 2026-11-02. Las comparaciones de esta sesión y sus muestras HTTP se registran aparte: no reemplazan esas fechas ni demuestran una nueva ingesta integral. Para repetir toda la ingesta desde cero todavía hace falta configurar una clave propia del Census. Las pruebas móviles realizadas son emulación de navegador, no uso de un teléfono físico.
