# Relación entre los 20 apartados del informe y el programa

| Capítulo | Evidencia implementada |
|---|---|
| 1–7 Portada, índice, resumen, problema, objetivos y justificación | Documentación del proyecto, límites declarados y asistencia preventiva |
| 8 Marco teórico y estado del arte | README, selección TF-IDF/Naive Bayes/LR/SVM y referencias |
| 9 Metodología CRISP-DM | Scripts separados para preparar, explorar, modelar, evaluar y desplegar |
| 10 Dataset | SpaPhish, auditoría de procedencia y etiquetas, hash SHA-256 |
| 11 EDA | `src/visualization/visualize.py` y `notebooks/01_exploracion.ipynb` |
| 12 Preprocesamiento | `src/data/make_dataset.py`, tokenización/TF-IDF dentro de Pipeline |
| 13 Diseño y selección del modelo | Grids, métricas CV y regla de selección en `src/models/train_model.py` |
| 14 Entrenamiento y ajuste | RandomizedSearchCV (modo completo), GridSearchCV (modo rápido), StratifiedGroupKFold, semilla 42 y exportación de parámetros |
| 15 Evaluación de resultados | Matriz de confusión, accuracy, precisión, recall, F1, ROC-AUC y PR |
| 16 Discusión de resultados | Análisis agregado FP/FN sin texto, límites del correo vs. canales no evaluados, informe automático |
| 17 Conclusiones | Solo completar conclusiones cuantitativas después de la ejecución real |
| 18 Trabajo futuro | Documentación; OCR, URL analysis real y modelos transformers **no** implementados |
| 19 Referencias | README, fuente pública y licencias |
| 20 Anexos | Tests, notebooks, manual VS Code, pruebas, esquemas y archivos de configuración |

**Importante:** La interfaz implementa análisis textual; NO tiene conectores a WhatsApp, correo, bancos, captura de pantalla, OCR ni análisis de reputación de URL. Esos componentes son propuestas futuras, no funciones actuales.

**Compatibilidad Python 3.14.5:** usar el intérprete Python 3.14 ya instalado y las dependencias compatibles incluidas en `requirements.txt`. Se mantiene la biblioteca científica real: scikit-learn.
