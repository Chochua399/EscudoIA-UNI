# EscudoIA — lista de comprobación final para la exposición

**Naturaleza del proyecto:** asistente académico de advertencia de posible phishing en español. No certifica la seguridad de un mensaje.

## Evidencias imprescindibles

- [ ] SpaPhish v5 descargado desde el sitio oficial de Mendeley, con referencia y licencia CC BY 4.0.
- [ ] Auditoría de carga: tamaño inicial, etiquetas, nulos, deduplicación y SHA-256 del archivo.
- [ ] Siete figuras EDA generadas por código (no copiadas de terceros).
- [ ] Comparación de Naive Bayes Multinomial, Regresión Logística y SVM lineal con TF-IDF.
- [ ] Validación cruzada; conservar los grupos de plantillas para evitar fugas.
- [ ] Evaluación del clasificador seleccionado en test reservado con accuracy, precisión, recall, F1 y matriz de confusión.
- [ ] Análisis de falsos positivos y falsos negativos.
- [ ] Artefacto entrenado en `models/modelo_estafas_v1.joblib`.
- [ ] Interfaz Streamlit con un caso benigno y un caso sospechoso; confirmar que no abre enlaces.
- [ ] Ejecución de pruebas automáticas y una captura del resultado.
- [ ] Copiar los resultados medidos de `reports/RESUMEN_REAL_PARA_INFORME.md` al informe final; revisar conclusiones para que reflejen los valores obtenidos.

## Capturas recomendadas (realizadas por el estudiante en su ordenador)

1. VS Code con carpetas `src`, `notebooks`, `app`, `tests` y `reports`.
2. Datos del proyecto mostrando el archivo CSV oficial cargado.
3. Entrenamiento con resultado exitoso.
4. Tabla de comparación entre los tres algoritmos.
5. Matriz de confusión y métricas numéricas del test.
6. Gráficos EDA y observaciones de calidad.
7. Una predicción de ejemplo y las señales explicadas.
8. Resultado de `py -3.14 main.py pruebas`.

## Qué NO afirmar

- No afirmar que la clasificación de un mensaje equivale a prueba legal de estafa.
- No afirmar que el modelo valida remitentes, bancos o URLs reales.
- No atribuir precisión al modelo si no se ha entrenado con el CSV oficial.
- No presentar métricas de las pruebas sintéticas como evidencia del estudio.
- No afirmar generalización a WhatsApp, SMS, Nicaragua o mensajes futuros sin un conjunto de evaluación externo.

**Referencia del corpus:** Bustio-Martínez y colaboradores (2026). *SpaPhish: A Spanish Dataset for Phishing and Psychological Pattern Detection*, versión 5. https://doi.org/10.17632/hz2d6gz7pc.5

## Publicación para el docente (obligatoria si se entrega por GitHub)

- [ ] `py -3.14 main.py todo` ejecutado con SpaPhish original (sin `--rapido`).
- [ ] `py -3.14 main.py verificar` terminó correctamente.
- [ ] `py -3.14 main.py publicar` generó la carpeta `ESCUDOIA_LISTO_PARA_GITHUB`.
- [ ] En GitHub están `models/modelo_estafas_v1.joblib`, `reports/metrics/resultados.json` y siete PNG de EDA.
- [ ] En Streamlit Community Cloud se seleccionó `app/app.py` y Python 3.14.
- [ ] Se probó el enlace en incógnito, con modelo y gráficos visibles.
- [ ] Se guardaron enlaces de GitHub y de Streamlit para el profesor.
