# Filadelfia · sistema de información

**Grupo:** David Restrepo — Curaduría y modelado de datos · Camila Martínez — Ingeniería de datos y pipelines ETL · Miguel Gómez — Desarrollo de interfaz y frontend · Sebastián Castaño — Ciberseguridad y gobernanza de privacidad

**Repositorio:** https://github.com/CamsMars/GD_PROYECTO  
**Aplicación:** https://gd-proyecto-v6.vercel.app  
**Revisado:** 2026-11-02

## Para quién y qué pregunta

Este proyecto busca organizar información pública de la ciudad de Filadelfia para explorar algunas diferencias entre sus distritos de planificación. La idea no era solamente reunir datos de distintas fuentes, sino integrarlos de manera que permitieran hacer comparaciones y responder preguntas concretas sobre movilidad, accidentalidad y condiciones socioeconómicas.

- **Usuario:** personas interesadas en consultar y comparar información territorial de Filadelfia, especialmente sobre movilidad, seguridad vial y condiciones socioeconómicas.
- **Preguntas:**
  1. ¿Los distritos que tienen más reportes de problemas en las vías a través de Philly311 por habitante también presentan una mayor tasa de accidentes graves por habitante?
  2. ¿Qué distritos tienen la mayor y la menor densidad de paraderos de SEPTA por kilómetro cuadrado?
  3. ¿Los distritos con menores ingresos tienen mayores tiempos de respuesta a los reportes viales de Philly311?
- **Escala y comparación:** trabajamos con los 18 distritos de planificación de Filadelfia. Para hacer las comparaciones, agregamos la información de las fuentes a esta escala territorial. Algunas preguntas utilizan tasas por habitante y otras indicadores por kilómetro cuadrado o medidas de ingreso.
- **Lo que decidimos no mostrar, y por qué:** no publicamos coordenadas exactas, direcciones, descripciones de texto libre ni identificadores que pudieran permitir reconocer a una persona o una solicitud específica. El objetivo del sistema es comparar información territorial, por lo que no necesitamos exponer registros individuales. Tampoco presentamos las relaciones estadísticas como si demostraran una causa: los resultados permiten identificar patrones, pero no explicar por sí solos por qué ocurren.

## La réplica

Tomamos como referencia el proyecto de ejemplo y conservamos su idea principal: integrar fuentes distintas mediante una arquitectura por capas y organizar los resultados para que puedan consultarse desde una interfaz. Sin embargo, no todas las fuentes de Filadelfia estaban disponibles de la misma manera, así que tuvimos que adaptar los procesos de consulta y descarga.

La arquitectura quedó organizada en tres capas: **Bronze, Silver y Gold**. En Bronze almacenamos los datos obtenidos de las fuentes; en Silver realizamos la limpieza, transformación y preparación de la información; y en Gold dejamos los datos agregados que utiliza la aplicación. Esta separación nos permitió trabajar con las fuentes por separado y después integrar los resultados sin mezclar los datos originales con los indicadores finales.

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

La licencia de los datos no debe confundirse con la de las herramientas utilizadas para construir el sistema. Para la interfaz usamos HTML, JavaScript nativo y Leaflet.js, esta última bajo licencia BSD-2-Clause ([texto oficial de Leaflet 1.9.4](https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE)). Durante el desarrollo también evaluamos Streamlit, que utiliza licencia Apache 2.0, pero finalmente no fue la herramienta elegida para la versión publicada.

## Bitácora de exploración

Durante el desarrollo probamos distintas formas de obtener, transformar y presentar la información. No todas funcionaron desde el primer intento. Esta tabla recoge los principales tramos del proceso y qué aprendimos de cada uno.

| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto | Qué resolvió | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| F01 · Distritos | Fuente de datos de Filadelfia y proceso de ingesta | Consulta de los límites de los distritos | City of Philadelphia License | Lago de datos | Sí, mediante el proceso de construcción del lago | Integrada | Define las 18 unidades territoriales de análisis | No resuelve por sí sola las diferencias entre las demás fuentes | Sí, porque permite utilizar una escala territorial común |
| F02 · Philly311 | API de Carto SQL | Consulta a la API y selección de los reportes viales | City of Philadelphia License | Lago de datos | Sí | Integrada | Permite analizar las solicitudes de servicio relacionadas con problemas viales | No permite explicar por sí sola las causas de los reportes ni las diferencias en los tiempos de atención | Sí, porque aporta información para las preguntas 1 y 3 |
| F03 · Accidentes | Fuente de registros de siniestros viales | Descarga y transformación de los registros | City of Philadelphia License | Lago de datos | Sí | Integrada | Permite comparar la accidentalidad entre distritos | No representa directamente el volumen de tráfico que circula por cada zona | Sí, porque permite construir el indicador de siniestralidad |
| F04 · SEPTA | Archivos GTFS | Descarga y procesamiento de los archivos comprimidos | SEPTA License Agreement | Lago de datos | Sí | Integrada | Permite identificar y contar los paraderos del sistema de transporte | No describe por sí sola la frecuencia o calidad del servicio | Sí, porque permite calcular la densidad de paraderos |
| F05 · ACS | API REST del U.S. Census Bureau | Consulta a la API y variable `CENSUS_API_KEY` | Dominio público federal | Lago de datos | Sí | Integrada | Aporta información demográfica y socioeconómica | Los datos agregados no representan todas las características de cada persona | Sí, porque permite contextualizar los indicadores por distrito |
| F06 · TIGER/Line | Shapefiles de Pensilvania 2024 | Descarga y procesamiento de información geográfica | Dominio público federal | Lago de datos | Sí | Integrada | Permite relacionar información geográfica y territorial | No aporta por sí sola indicadores sociales o de movilidad | Sí, porque facilita las relaciones espaciales |
| F12 · Fuente escolar | Consulta a la fuente | Acceso al servidor y revisión de sus condiciones de uso | No suficientemente clara | No se incorporó al lago | No aplica | Descartada | Permitió identificar una posible fuente adicional | Los tiempos de espera y la falta de claridad sobre la licencia impidieron integrarla | No, porque no cumplía las condiciones necesarias para incorporarla |

## Protección

**Nivel:** solo agregados.

Desde el inicio decidimos que la aplicación debía permitir consultar información territorial sin exponer registros que pudieran identificar directamente a una persona. Esto fue especialmente importante para los datos de Philly311, porque las solicitudes pueden contener información sobre lugares y situaciones particulares.

- **Qué protegemos, y de quién:** protegemos la información que podría facilitar la identificación de personas a partir de los registros originales. La aplicación está pensada para mostrar indicadores por distrito, no para consultar solicitudes individuales.
- **Pruebas de terminal o de ventana privada:** ejecutamos `verificar_privacidad.py` sobre los seis archivos publicados:
  - `demografia_distritos.csv`
  - `indicadores_distrito.csv`
  - `paraderos_septa.csv`
  - `reportes_viales_311.csv`
  - `siniestralidad_vial.csv`
  - `tracts_distritos.csv`

  La ejecución terminó con el mensaje:

  `OK: no hay coordenadas, direcciones, texto libre ni IDs en los archivos publicados`

  Esta comprobación permite verificar que esos campos no aparecen en los archivos revisados. Sin embargo, no significa que cualquier posibilidad de inferencia o reidentificación haya desaparecido. La agregación reduce la exposición de información, pero no elimina todos los riesgos posibles.
- **Revisión de secretos en el historial:** la clave `CENSUS_API_KEY` se mantiene en el archivo local `.env`, que está incluido en `.gitignore`. Para que otra persona pueda configurar el proyecto se dejó `.env.ejemplo` como plantilla, sin incluir la clave real. También revisamos que la clave no quedara expuesta en los archivos publicados ni en el repositorio.

No se conserva evidencia reproducible del supuesto cruce con OPA. Se retira esa afirmación y no se presenta como una prueba realizada.

## Herramienta elegida para las vistas

- **Qué necesitábamos mostrar:** indicadores por distrito, comparaciones entre territorios y resultados de las tres preguntas del proyecto. La información debía poder consultarse de forma sencilla, sin que el usuario tuviera que conocer cómo se construyó el lago de datos.
- **Qué teníamos que proteger:** los archivos publicados no debían exponer los registros originales ni los campos que habíamos decidido excluir por privacidad.
- **Por qué esta herramienta cumple las dos cosas, y cuál descartamos por poco:** finalmente utilizamos HTML, JavaScript nativo y Leaflet.js para construir una aplicación estática. La desplegamos en Vercel y dejamos la interfaz separada de los procesos de ingesta y transformación. Esto nos permitió publicar las vistas sin mantener un servidor Python activo para atender las consultas de la aplicación.

El README anterior menciona una alternativa Streamlit, pero el historial disponible no contiene prototipo, comandos de ejecución ni capturas. El usuario confirmó que no conserva capturas. Por eso no se afirma una prueba comparada completada. Ver `evidencia/comparacion_visualizacion.md`.

## Nuestra posición

**Gestión y gobierno de datos**

Durante el proyecto entendimos que tener acceso a una fuente pública no significa que podamos utilizarla de cualquier manera. Cada fuente tiene condiciones, formatos y niveles de calidad diferentes. Por eso fue necesario revisar su procedencia, documentar las condiciones de uso y decidir cuáles podían incorporarse al sistema.

La arquitectura por capas también responde a esa necesidad. No queríamos mezclar los datos tal como llegan de las fuentes con los indicadores que finalmente mostramos. Separar la ingesta, la transformación y los resultados facilita revisar de dónde viene la información y cómo se obtuvo. Aun así, los resultados dependen de la calidad y disponibilidad de las fuentes originales.

En el análisis encontramos que la relación entre los reportes viales por habitante y los accidentes graves por habitante fue muy baja (Spearman ρ = -0.105; p = 0.677). Para la relación entre ingreso mediano y tiempos de respuesta de Philly311 obtuvimos ρ = 0.191 y p = 0.447. En ninguno de los dos casos encontramos evidencia estadística suficiente para afirmar que existe una asociación. Esto no demuestra que no haya ninguna relación; significa que, con los datos y el alcance de este análisis, no podemos sostener esa conclusión.

También encontramos diferencias importantes en la densidad de paraderos: Center City (CTR) presentó el valor más alto, con 48.1 paraderos por km², mientras que Lower South (LS) tuvo el más bajo, con 2.5 paraderos por km².

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
| Revisión documental y técnica, 2026-11-02 | Codex | Aplicar correcciones con evidencia existente | Ajustes de README, Excel, periodos y controles | Alcance y resultados en `evidencia/revision_entrega2.md`; no atribuye al equipo pruebas no conservadas |

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
