# Correcciones de la segunda entrega

Fecha de revisión: 2026-11-02. Base: commit `6d7e150` de CamsMars/GD_PROYECTO.

## Aplicado

- README: instalación desde `cd GD_PROYECTO`, plantilla `.env.ejemplo` restaurada, bitácora con los cinco registros reales del Excel y una entrada sobre esta corrección. Se retiraron afirmaciones de pruebas sin respaldo conservado.
- Leaflet 1.9.4: BSD-2-Clause, según su LICENSE oficial. Streamlit queda documentado como alternativa mencionada cuya ejecución histórica no se pudo confirmar. El usuario confirmó que no conserva capturas; no afirmó que nunca se hubiera probado.
- Excel: solo F01–F06 en el catálogo activo; las otras siete fuentes se conservaron en `fuentes_no_integradas.json`. Se mantuvieron las cinco hojas y las fórmulas del resumen. Se corrigió `geometry` al nombre real del campo y se comprobó que los 28 campos documentados coinciden con todos los campos del lago.
- Philly311: conserva selección UTC 2020–2024 y 181.699 filas. Tres fechas convertidas a America/New_York resultan 2019-12-31. Se hizo visible esta salvedad en los metadatos.
- SEPTA: se identifica como feed descargado el 2026-11-02. No se le atribuye cobertura 2020–2024 ni un calendario no conservado. La ingesta ahora guarda los rangos de calendar.txt y calendar_dates.txt cuando se vuelva a ejecutar.
- F05: se copió el enlace literal del campo `license` del metadato oficial de ACS, dejando la explicación del equipo sobre dominio público separada de esa cita.
- Web: enlaces originales en botones Fuente y tabla; respuestas estadísticas sin afirmar que una asociación inexistente haya sido demostrada; controles táctiles de 44 px y ajustes para pantallas estrechas.
- Privacidad: se inspeccionan propiedades de todas las entidades GeoJSON, se rechazan archivos de datos web inesperados y se expresa el alcance real del control. Se ocultan claves también en mensajes de error de ingesta.
- Verificación de fuentes: devuelve un estado de error cuando fallan las fuentes integradas, y crea su carpeta de evidencia. La reconstrucción ejecuta además los controles de integridad.

## Pruebas realizadas en esta revisión

1. Reconstrucción con `python construir_lago.py` desde las tablas conservadas: correcta. No se repitió la ingesta completa ni se usó una clave Census.
2. `python verificar_privacidad.py`: correcto para seis CSV y dos GeoJSON; no se encontraron columnas de la lista prohibida. Se permite geometría de distritos e identificadores territoriales y de paraderos, que no son IDs de personas.
3. `python verificar_entrega.py`: 18 distritos, 408 tracts, 1.579.706 habitantes, 181.699 solicitudes, 36.303 siniestros, 7.987 paraderos; claves y cuatro indicadores contrastados para los 18 distritos. P1: rho=-0,105; P3: rho=0,191, coinciden con los resultados guardados.
4. Sintaxis JavaScript y shell: correcta.
5. Búsqueda de patrones de claves Census largas en archivos de texto de las nueve revisiones del historial: sin coincidencias. No es una auditoría universal de secretos.
6. HTTP en web publicada: portada y catálogo devuelven 200; `.env`, `config.py`, `lago/reportes_viales_311.csv` y `datos_crudos/f04_gtfs_public.zip` devuelven 404. Detalle en `publicacion_http.json`. Estas pruebas corresponden a la versión remota anterior a publicar los cambios locales.
7. Excel: comparación de valores y fórmulas con el original, recalculado del resumen (6 fuentes integradas, 28 campos, 5 registros IA) y revisión visual de los rangos modificados. Candidatas y descartadas no figuran como fuentes activas del lago.

## Pendientes concretos

- Evidencia de dos herramientas probadas: no hay prototipo Streamlit recuperable en el historial. La tabla comparativa es documental, no una prueba ejecutada. Si el requisito exige ejecución, todavía falta ejecutar y registrar ese segundo prototipo.
- Prueba visual y funcional de móvil: el navegador integrado no pudo abrir una sesión de prueba. Los cambios adaptables se revisaron en el código, pero no se certifica uso desde teléfono, mapa, filtros ni interacción Fuente en navegador.
- Licencias de F01–F04 y texto de F06: se conservaron las declaraciones existentes del equipo; no se atribuye a esta revisión una nueva validación completa de los términos de cada portal.
- Publicación en GitHub y Vercel: la conexión local de GitHub no tiene una credencial válida. Los cambios están preparados localmente; aún no aparecen en la web remota.

El repositorio sigue conteniendo registros individuales sin identificadores directos. La web muestra agregados. Este trabajo no certifica anonimato ni reconstrucción idéntica después de descargar fuentes cambiantes.


## Actualización posterior: mapa y tamaños de pantalla

Se sustituyó CARTO por el mapa estándar de OpenStreetMap sin clave, conservando
la atribución visible y el almacenamiento normal en caché del navegador.
El título de escritorio pasó de un máximo de 72 px a 36 px; en móvil es de 24 px.
También se contuvo el ancho mínimo de las tarjetas para que las tablas no
ensanchen la página, y se recuperaron los estilos de leyenda, fichas y barras
al integrar el diseño remoto con las correcciones de esta entrega.

Pruebas locales realizadas en navegador:

- Anchos 320, 390, 768 y 1440 px: ancho del documento igual al de la vista.
- Fondo OpenStreetMap: imágenes cargadas y atribución visible.
- 18 polígonos interactivos; selección de distrito muestra su ficha.
- Cambio de indicador a paraderos y apertura/cierre de Fuente correctos;
  la ventana contiene F04/F01, enlaces, licencia, periodo y fecha.
- Sin errores de consola detectados durante estas interacciones.

Esto sustituye el pendiente anterior por falta de una sesión de navegador.
La prueba es una emulación de tamaños móviles; no se atribuye una prueba con
un teléfono físico ni una nueva comparación con Streamlit.
