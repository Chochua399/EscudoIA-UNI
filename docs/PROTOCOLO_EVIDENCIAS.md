# Protocolo de evidencias para el informe ampliado de 72 páginas

Este archivo indica qué capturar en Visual Studio Code y qué resultados copiar al informe. Está organizado por secciones de la guía del docente. **No inventes resultados si aún no se ha ejecutado SpaPhish.**

| Sección del informe | Evidencia verificable | Archivo o captura |
|---|---|---|
| 1–7 | Portada, índice, problema, objetivos, justificación | Informe Word ampliado |
| 8 | Marco teórico | Referencias y diseño de tres clasificadores |
| 9 | Metodología | Árbol de archivos, `README.md`, CRISP-DM |
| 10 | Descripción del dataset | `auditoria_dataset.json`, información de licencia, SHA256 |
| 11 | Análisis EDA | Siete figuras de `reports/eda/`, nulos y términos frecuentes |
| 12 | Preprocesamiento | `make_dataset.py`, archivo processed y comparación de registros |
| 13 | Selección de modelos | Configuraciones y tres pipelines desde `train_model.py` |
| 14 | Entrenamiento y ajuste | CSV de búsquedas, semillas, parámetros, n.º de pliegues |
| 15 | Evaluación | `resultados.json`, matriz de confusión, curvas ROC/PR, Brier |
| 16 | Discusión | `analisis_errores_sin_texto.json`, limitaciones de generalización |
| 17 | Conclusiones | Solo concluir después de revisar resultados reales |
| 18 | Trabajo futuro | Pautas de mejora, no afirmar que OCR/WhatsApp están implementados |
| 19 | Referencias | Dataset, scikit-learn, Streamlit y publicaciones del informe |
| 20 | Anexos | Notebooks, código, capturas de app, pruebas `pytest`, README |

## Secuencia de capturas

1. Terminal VS Code: `py -3.14 --version` y verificación de bibliotecas.
2. Explorador de VS Code con carpetas del proyecto y cuatro notebooks.
3. Terminal `main.py todo` después de descargar SpaPhish.
4. `auditoria_dataset.json` para mostrar filas originales, retenidas y duplicados.
5. Gráficos del EDA y tabla de términos.
6. Tabla `comparacion_validacion.csv` con tres modelos (CV, no test).
7. `matriz_confusion.png` y curvas de la evaluación final del ganador.
8. `RESUMEN_REAL_PARA_INFORME.md` y `analisis_errores_sin_texto.json`.
9. Interfaz Streamlit con un mensaje **ficticio** y resultado orientativo.
10. Terminal de `pytest` con pruebas aprobadas.

## Interpretación de las métricas

- FP: mensaje real legítimo marcado como phishing. FN: phishing real no identificado.
- Priorizar F1 y recall no implica desatender los falsos positivos.
- Un F1 ≥ 0.80 era una **meta**, nunca una garantía.
- Los porcentajes son válidos para el CSV y su partición, no para todas las estafas ni todos los canales.

## Registro recomendado del equipo

Fecha, integrantes, versión CSV, DOI, hash SHA-256, versión Python, scikit-learn, modo de búsqueda, semillas, parámetros ganadores, tabla CV, métricas test, análisis de errores, capturas.
