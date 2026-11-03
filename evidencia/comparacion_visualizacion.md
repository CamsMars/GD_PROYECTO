# Streamlit frente a HTML/JS/Leaflet: prueba real

Fecha de la sesión: 2026-11-03. Prueba nueva de cierre; no se atribuye al desarrollo histórico anterior.

## Datos y versiones

Las dos vistas leen exactamente `docs/datos/distritos.geojson`, `fuentes.json` y `preguntas.json`, con los 18 distritos agregados. Los hashes de esos archivos y las versiones están en [resultados.json](exploracion_2026-11-03/resultados.json).

- HTML/JS: aplicación de `docs/`, Leaflet 1.9.4 y fondo OpenStreetMap.
- Streamlit 1.66.1: [prototipo conservado](../exploracion/vistas_streamlit.py), también con Leaflet 1.9.4 y OpenStreetMap dentro de un iframe.

Se comparó el marco de aplicación y publicación. No se afirma que sean dos motores de mapas distintos.

## Comandos y procedimiento

Instalar `requirements-exploracion.txt` y ejecutar `python exploracion/comparar.py` desde la raíz. Para abrir ambas vistas, usar el servidor HTTP de `docs/` en el puerto 8765 y el comando de Streamlit del [procedimiento reproducible](../exploracion/README.md) en el puerto 8501.

En navegador se seleccionó Población y Central Northeast (CNE), se comprobó el mapa y se abrieron las fuentes. Después se compararon ambas vistas a 390 × 844 px. Las observaciones están en [navegador.json](exploracion_2026-11-03/navegador.json).

## Resultados observados

| Criterio común | HTML/JS/Leaflet | Streamlit |
|---|---|---|
| Datos | Mismos tres archivos agregados | Mismos tres archivos agregados |
| Mapa real | 18 polígonos; fondo OSM cargado y atribuido | 18 polígonos dentro del iframe; mismo fondo y atribución |
| Valor de población en CNE | 83.860 | 83,860; mismo valor, distinto separador visual |
| Cambio de indicador | Selector operativo | Selector operativo |
| Selección territorial | El clic de mapa actualiza la ficha | El selector Distrito actualiza la ficha; el clic del mapa solo abre un rótulo |
| Prueba de ese límite | Clic en CNE: ficha CNE | Clic en CTR: rótulo «Central (CTR): 140361»; la ficha siguió en CNE, 83,860 |
| Fuente F05 | Diálogo con vigencia, fecha y enlace a ficha pública | Expansor con los mismos metadatos y enlace público |
| Vista móvil de 390 px | Documento de 390 px, diálogo de 352 px | Documento de 390 px, iframe de 358 px |
| Errores de consola observados | Ninguno en estas interacciones | Ninguno en estas interacciones |
| Valores del prototipo | La verificación numérica contrasta los indicadores publicados | AppTest verificó 108 combinaciones: 18 distritos × seis indicadores |
| Publicación necesaria | Archivos estáticos; sitio existente en Vercel | Servidor Python local durante la prueba; no se probó su nube |

Las pruebas de escritorio se capturaron a 1280 × 720 px (HTML) y 1440 × 1000 px (Streamlit). La comparación móvil sí se hizo al mismo tamaño, 390 × 844 px. No se midieron rendimiento sostenido ni costes de alojamiento.

## Capturas reales

| Vista | Captura |
|---|---|
| HTML en escritorio | [Abrir](exploracion_2026-11-03/prueba_html_escritorio.jpg) |
| Streamlit en escritorio | [Abrir](exploracion_2026-11-03/prueba_streamlit_escritorio.jpg) |
| HTML en móvil emulado | [Abrir](exploracion_2026-11-03/prueba_html_movil.jpg) |
| Streamlit en móvil emulado | [Abrir](exploracion_2026-11-03/prueba_streamlit_movil.jpg) |

## Decisión después de la prueba

Se mantiene HTML/JS/Leaflet en producción: conserva el alojamiento estático ya configurado y la ficha conectada al clic del mapa. Streamlit funcionó con los mismos datos y queda como alternativa ejecutable, pero el prototipo necesita un proceso Python y una interacción distinta para cambiar la ficha. Esa diferencia pertenece a este prototipo: no se afirma que Streamlit sea incapaz de implementarla de otra forma.

Streamlit tiene licencia Apache-2.0 y Leaflet 1.9.4 BSD-2-Clause. Las referencias están en [exploracion/README.md](../exploracion/README.md). No se publicó una clave del Census ni se enviaron registros individuales a otro servicio de visualización.
