# Guion de demostración (5–8 minutos)

1. **Problema:** recibir una solicitud digital inesperada y difícil de verificar. EscudoIA ofrece una segunda opinión de texto.
2. **Fuente:** mostrar licencia, año, clases y versión en la pantalla Datos. Aclarar que SpaPhish es email y no representa necesariamente el habla nicaragüense.
3. **EDA:** mostrar distribución real y longitud de mensajes. Explicar por qué una URL por sí sola no prueba fraude.
4. **Preprocesamiento:** identificar en VS Code `src/data/make_dataset.py`, deduplicación y hash de plantillas para evitar fuga.
5. **Modelos:** enseñar `reports/metrics/comparacion_validacion.csv` y justificar TF-IDF + tres modelos.
6. **Validación:** abrir `reports/figures/matriz_confusion.png` y explicar falso negativo y falso positivo.
7. **Interfaz:** pegar un ejemplo ficticio, explicar señales lingüísticas y advertencias.
8. **Ética:** no guardar mensajes, no abrir enlaces, resultados orientativos, no verificación de remitente.

## Preguntas posibles

**¿Por qué no usar ChatGPT?** Porque el proyecto evalúa clasificación supervisada sobre un corpus etiquetado, métricas reproducibles y modelos livianos.

**¿Por qué no afirmar seguridad con riesgo bajo?** Porque un falso negativo es posible y el clasificador solo analiza patrones de texto.

**¿Por qué se reserva un test independiente?** Para no optimizar sobre los ejemplos usados para medir generalización.

**¿Por qué SpaPhish y no un dataset en inglés?** Porque SpaPhish está documentado y nativamente redactado en español; aún se requiere una validación local.

**¿Qué significa F1?** Media armónica de precisión y recall, útil para equilibrar falsas alarmas y amenazas omitidas.

**¿Qué sigue si el modelo no logra la meta F1≥0,80?** Analizar errores y limitaciones; no modificar manualmente las métricas ni forzar el resultado.
