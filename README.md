# EscudoIA — versión de entrega GitHub + Streamlit (Python 3.14.5)

**La entrega pública se construye después de entrenar con SpaPhish v5.** Si subes el proyecto de desarrollo sin entrenar, al profesor le aparecerá “Modelo pendiente”.

Desde VS Code en la carpeta donde está `main.py`:

```powershell
py -3.14 main.py todo
py -3.14 main.py verificar
py -3.14 main.py publicar
```

El último comando crea **`ESCUDOIA_LISTO_PARA_GITHUB/`** y **`ESCUDOIA_LISTO_PARA_GITHUB.zip`**. Sube el contenido de esa carpeta al repositorio, porque **sí lleva el modelo entrenado y las evidencias**, sin copiar el CSV original ni mensajes de usuarios. Después crea tu aplicación en Streamlit Community Cloud con `app/app.py` y Python `3.14`.

Si aún no descargaste SpaPhish, abre [la página oficial v5](https://data.mendeley.com/datasets/hz2d6gz7pc/5), guarda su CSV en `data/raw/`, o cárgalo desde la sección “Entrenar IA” de la aplicación.

Lee **`docs/PUBLICAR_GITHUB_STREAMLIT.md`** para los pasos completos. La ejecución local funciona con `py -3.14 main.py` (no reinstala Python). Para realizar notebooks y pruebas en otra computadora, instala las herramientas opcionales con `py -3.14 -m pip install -r requirements-dev.txt`.

**Transparencia:** las pruebas incluidas usan datos sintéticos solo para verificar código. No se proporciona un modelo entrenado con SpaPhish hasta que el propietario descargue y entrene sobre el CSV original. Las predicciones son orientativas y no verifican remitentes.

---

# ESCUDOIA — VERSIÓN MEJORADA PARA ENTREGA (Python 3.14.5)

**Ya puedes ejecutar este proyecto con el Python 3.14.5 instalado en tu equipo.**
No necesitas reinstalar Python ni crear un entorno virtual si las bibliotecas ya están instaladas.

```powershell
py -3.14 main.py
```

Abre <http://localhost:8501>. En la barra izquierda encontrarás ahora **Entrenar IA** y **Preparar entrega**.

1. Descarga el CSV de [SpaPhish v5](https://data.mendeley.com/datasets/hz2d6gz7pc/5), o prueba el botón de descarga automática desde la sección **Entrenar IA**.
2. Carga el CSV (se guarda en `data/raw/`).
3. Ejecuta EDA + entrenamiento de los tres clasificadores desde la sección **Entrenar IA**. Usa primero el modo rápido para verificar y luego el protocolo completo de cinco pliegues para el informe.
4. Consulta **Resultados y EDA** y descarga las evidencias desde **Preparar entrega**.
5. Comprueba las pruebas automáticas ejecutando `py -3.14 main.py pruebas` en VS Code.

**Ejecución alternativa desde la terminal (sin abrir otro programa):**
```powershell
py -3.14 main.py todo --rapido
py -3.14 main.py todo
py -3.14 main.py estado
```

Lee `EMPIEZA_AQUI_PYTHON_314.txt` y `docs/CHECKLIST_ENTREGA_FINAL.md`.

> **Nota de rigor:** el código y los tests se verificaron con un conjunto sintético exclusivamente para comprobar la ejecución; el paquete no incluye SpaPhish ni métricas experimentales hasta que cargues y entrenes con el CSV real. La descarga automática puede no estar disponible según la respuesta de Mendeley; la carga manual siempre es una alternativa.

---

# ESCUDOIA — Asistente inteligente para detectar posibles estafas digitales

**Proyecto de curso de Inteligencia Artificial · Ingeniería de Sistemas · UNI (Nicaragua)**

Esta es la **implementación integral** del informe académico ampliado *Asistente inteligente para la detección de posibles estafas digitales en mensajes en español mediante procesamiento de lenguaje natural*. Es el proyecto científico con bibliotecas originales, **NO** una simulación basada en reglas.

**Compatible por diseño con Windows, Visual Studio Code y tu Python 3.14.5.** No hay que desinstalar Python ni instalar Python 3.11/3.12. Sí es necesario instalar las bibliotecas del proyecto con `pip` (pandas, NumPy, scikit-learn, Streamlit, etc.), como corresponde a un programa real de IA.

## 1. Abrir el proyecto en Visual Studio Code, sin cambiar Python

Extrae el ZIP y abre desde VS Code **esta misma carpeta**, que contiene `main.py` y `requirements.txt`. Usa Terminal > New Terminal (PowerShell):

```powershell
py -3.14 --version
py -3.14 -m pip install -r requirements.txt
py -3.14 scripts\VERIFICAR_ENTORNO.py
```

**No es necesario crear un entorno virtual** en tu equipo: ya instalaste Python 3.14.5 y sus bibliotecas; ejecuta `py -3.14 main.py`.

Para seleccionar el intérprete en VS Code: `Ctrl+Shift+P` → `Python: Select Interpreter` → selecciona el Python 3.14 instalado en Windows. Instala las extensiones Microsoft **Python** y **Jupyter** solo si deseas ejecutar/depurar notebooks desde el editor.

## 2. Iniciar el programa con interfaz web

```powershell
py -3.14 main.py
```

La interfaz se abrirá en `http://localhost:8501`. Si el navegador no se abre automáticamente, entra a esa dirección. Puedes usar `Simple Browser: Show` en VS Code. Para detener el servidor, enfoca la terminal y presiona `Ctrl+C`.

**Antes de entrenar:** la aplicación muestra *señales educativas basadas en reglas*, identificadas como demostración; no falsifica un modelo entrenado ni muestra métricas inventadas. **Después de entrenar:** aplica el clasificador real serializado en `models/`.

## 3. Datos reales: SpaPhish, la fuente indicada en el informe

- SpaPhish v5: https://data.mendeley.com/datasets/hz2d6gz7pc/5
- DOI: 10.17632/hz2d6gz7pc.5; licencia CC BY 4.0.
- La publicación describe **1.395 correos en español: 731 phishing y 664 legítimos**. Esto describe la fuente; el programa informa por separado los ejemplos que sobrevivan a la limpieza.
- Descarga el archivo **CSV** oficial e introdúcelo en `data/raw/` (separado por `;` en la distribución publicada; el lector admite también coma/tabulación). No lo edites ni lo renombres obligatoriamente: con un solo CSV, el programa lo detecta automáticamente.
- Variables mínimas: `subject`, `body`, `Label` (admite 000/001 y 0/1). Las variables técnicas o de persuasión se exploran si existen, pero **NO** se utilizan como predictores del clasificador principal, pues la interfaz recibe únicamente texto.
- El proyecto **no incluye el dataset**, ni hace conexiones automáticas a mensajes o correo personal.

Si pones más de un CSV en `data/raw`, ejecuta comandos con `--input "data/raw/NOMBRE.csv"`.

## 4. Ejecutar todas las fases del proyecto

Detén temporalmente la aplicación con `Ctrl+C` y escribe:

```powershell
# Datos: limpieza, etiquetas, hash, prevención de fuga
py -3.14 main.py datos

# Análisis exploratorio, tablas y siete figuras
py -3.14 main.py eda

# Entrenamiento real de 3 modelos + CV + selección + evaluación
py -3.14 main.py entrenar

# Pruebas unitarias y de extremo a extremo
py -3.14 main.py pruebas

# Mostrar estado de dataset y modelo
py -3.14 main.py estado

# Reiniciar interfaz con el modelo entrenado
py -3.14 main.py
```

Puedes hacer las tres primeras etapas con **un solo comando**:

```powershell
py -3.14 main.py todo
```

Para un ensayo más corto antes de la ejecución final:

```powershell
py -3.14 main.py todo --rapido
```

**Modo rápido**: usa un espacio de búsqueda reducido y CV de 3 pliegues. **Modo completo**: emplea CV de 5 pliegues y `RandomizedSearchCV` de 18 configuraciones por candidato para explorar n-gramas, min_df, max_df, sublinear_tf y parámetros del clasificador. Los resultados pueden cambiar entre los dos modos; para el informe usa la ejecución completa con el CSV auténtico.

## 5. Diseño científico (capítulos 9–16 del informe)

**CRISP-DM:** comprensión del problema → datos → preparación → modelado → evaluación → despliegue.

- Se limpian etiquetas, valores nulos, duplicados exactos y registros textuales conflictivos; se conservan URLs, números, símbolos y expresiones de urgencia.
- Se agrupan posibles plantillas repetidas mediante huellas normalizadas y se separan usando `StratifiedGroupKFold`. Cerca de 80% queda en entrenamiento y 20% en prueba, según el balance de grupos.
- El `TfidfVectorizer` y cada modelo forman un único `Pipeline`: el vocabulario nunca se ajusta con la partición de prueba.
- Se comparan **MultinomialNB, LogisticRegression y LinearSVC** mediante validación cruzada sobre entrenamiento. F1 de phishing es la métrica principal; recall es el desempate; se considera LR en diferencias mínimas de F1 por su interpretabilidad.
- Después de elegir un único ganador, se ajusta una calibración sigmoide dentro de entrenamiento. Las probabilidades y los límites bajo/medio/alto son **orientativos**; los umbrales todavía son provisionales y no están certificados para producción.
- La evaluación final independiente del ganador incluye accuracy, precisión, recall, F1, matriz de confusión TN/FP/FN/TP, ROC-AUC, Average Precision y Brier Score, más revisión de errores sin publicar textos sensibles.
- Baseline adicional: `DummyClassifier` clase mayoritaria. Esto ayuda a determinar si la IA supera una estrategia ingenua.
- `random_state=42`, SHA-256 del CSV, versiones del ambiente, parámetros y resultados registrados en `reports/`.

**Importante para el profesor:** las métricas de los tres modelos comparables salen de la **validación cruzada**, no del conjunto de prueba. El conjunto de prueba se usa para evaluar **solo el ganador** y no debe reutilizarse para volver a elegir hiperparámetros.

## 6. Archivos de evidencia que se generan al ejecutar el CSV

| Ruta | Evidencia |
|---|---|
| `data/processed/mensajes_preparados.csv` | Datos de investigación, sujetos a no publicarse si contienen información sensible |
| `reports/metrics/auditoria_dataset.json` | Filas originales, descartar, duplicados, distribución, hash del CSV |
| `reports/eda/` | Siete gráficos, estadísticas de longitudes, nulos y términos frecuentes |
| `reports/metrics/busqueda_1.csv`...`busqueda_3.csv` | Ajustes probados de cada algoritmo, métricas de CV |
| `reports/metrics/comparacion_validacion.csv` | Tabla comparativa CV: accuracy, precision, recall y F1 |
| `reports/metrics/resultados.json` | Experimento con baseline, modelo ganador, test y parámetros |
| `reports/metrics/analisis_errores_sin_texto.json` | Patrones agregados de falsos positivos/negativos |
| `reports/metrics/predicciones_test_sin_texto.csv` | Solo IDs hash y etiquetas, sin cuerpo de correos |
| `reports/figures/` | Matriz de confusión, curva ROC y precisión-recall |
| `models/modelo_estafas_v1.joblib` | Modelo completo guardado para predicción |
| `models/metadata_modelo.json` | Fecha, dataset, versión scikit-learn, límites, evidencia |
| `reports/RESUMEN_REAL_PARA_INFORME.md` | Métricas generadas automáticamente para completar Word |

**Nunca incluyas resultados de pruebas sintéticas como si fueran resultados del corpus oficial.** El programa no puede comprobar por sí mismo que un archivo local sea SpaPhish solo por llamarse así: el equipo debe revisar su descarga, fuente y licencia.

## 7. Cuatro notebooks desde Visual Studio Code

En `notebooks/` encontrarás `01_exploracion.ipynb`, `02_preprocesamiento.ipynb`, `03_modelado.ipynb`, `04_evaluacion.ipynb`. Selecciona el kernel de Python 3.14 y usa *Run All*. El código reusable está en `src/`, no repetido en las celdas.

## 8. Pruebas

```powershell
py -3.14 -m pytest -q
```

Se prueban carga del CSV con separadores/BOM, etiquetas, eliminación de duplicados, ausencia de fuga por grupos, generación de EDA, entrenamiento de los tres clasificadores, predicción y manejo de mensajes cortos. El *end-to-end* utiliza únicamente mensajes sintéticos para validar ejecución, **no** rendimiento de SpaPhish.

## 9. Seguridad, ética y limitaciones

- La interfaz nunca visita enlaces sospechosos ni descarga adjuntos.
- No almacena por defecto los mensajes escritos por el usuario; la exportación del **resultado** requiere que el propio usuario pulse Descargar.
- La base experimental es **correo electrónico en español**. No significa que se hayan validado SMS, WhatsApp, habla regional nicaragüense, OCR, imágenes o campañas nuevas.
- Un resultado de riesgo bajo **NO** garantiza autenticidad o seguridad. Falsos positivos y falsos negativos son posibles.
- No introducir contraseñas reales, códigos OTP, números de tarjeta ni información privada en la interfaz.
- Solo cargar archivos `.joblib` entrenados localmente; no abrir modelos desconocidos porque Joblib usa serialización basada en pickle.
- El repositorio no debe publicarse con datos de usuarios, mensajes sensibles ni modelos serializados de fuentes no confiables.

## 10. Relación documental

El documento original tiene 20 secciones obligatorias del docente. La evidencia técnica y su correspondencia están en `docs/RELACION_CON_INFORME.md`. `docs/GUIA_PARA_DEFENSA.md` prepara la exposición. `docs/PROTOCOLO_EVIDENCIAS.md` enumera lo que debes recopilar para completar el Word sin inventar métricas.

### Referencias técnicas

- SpaPhish: https://doi.org/10.17632/hz2d6gz7pc.5
- scikit-learn 1.8: https://scikit-learn.org/1.8/
- Streamlit: https://docs.streamlit.io/get-started/installation/command-line
- pandas 2.3.3 y Python 3.14: https://pandas.pydata.org/docs/whatsnew/v2.3.3.html

---
**Entrega del código:** proyecto académico completo; la evaluación científica definitiva solo existe después de ejecutarlo con el CSV oficial y guardar las evidencias.
