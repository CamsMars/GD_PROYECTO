# Comparación de herramientas de visualización

Revisión documental: 2026-11-02. No es un registro de dos pruebas ejecutadas.

| Criterio | Streamlit | HTML/JS/Leaflet 1.9.4 |
|---|---|---|
| Evidencia conservada | Solo mención en README; sin prototipo ni comandos en el historial disponible. El usuario no conserva capturas. | `docs/index.html`, `app.js`, `estilos.css`, tres archivos de datos y configuración Vercel. |
| Entrada para una comparación válida | Los mismos 18 distritos e indicadores agregados | Los mismos 18 distritos e indicadores agregados |
| Licencia de herramienta | Apache-2.0: https://github.com/streamlit/streamlit/blob/develop/LICENSE | BSD-2-Clause: https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE |
| Despliegue previsto | Requiere proceso Python de la aplicación | Publicación estática de `docs/` |
| Decisión documentada | Alternativa mencionada, ejecución histórica sin confirmar | Implementación elegida y conservada |

Para completar una prueba comparada hay que ejecutar ambos prototipos con el mismo archivo agregado, registrar versiones, comandos, resultados y problemas de mapa, filtros, botones Fuente y ancho móvil. No se atribuyen tiempos, resultados ni dificultades a una prueba sin evidencia. La ausencia de capturas no demuestra que nunca se haya probado Streamlit.
