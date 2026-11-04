# Manual de uso de la aplicación EscudoIA

## Pantalla 1. Analizar mensaje

Introduce o pega únicamente texto en español, evitando datos personales. Hay mensajes ficticios incluidos para probar. Presiona **Analizar con inteligencia artificial** cuando el modelo ya esté entrenado. El sistema devuelve clase binaria, banda de riesgo provisional, señales lingüísticas y recomendaciones. Ninguna predicción demuestra la identidad del remitente.

**Antes de entrenar:** el botón indicará *demo sin IA* y solo identifica reglas lingüísticas. Para activar el modelo, importa el CSV SpaPhish desde la pantalla de datos y ejecuta el entrenamiento en VS Code.

## Pantalla 2. Resultados y EDA

Si existe `reports/metrics/resultados.json`, muestra el modelo seleccionado por validación cruzada, las métricas de prueba, falsos negativos/positivos, tabla CV de tres modelos y figuras. No editar manualmente estos resultados; vuelve a entrenar para producir nuevas evidencias.

## Pantalla 3. Datos del proyecto

Permite subir a `data/raw` un CSV del corpus oficial. No cargar correos de usuarios reales sin autorización. La subida no inicia automáticamente entrenamiento: debes ejecutar el comando desde VS Code. Puedes consultar la auditoría cuando exista.

## Pantalla 4. Cómo funciona

Describe CRISP-DM, preprocesamiento, TF-IDF, Naive Bayes, Regresión Logística, SVM, evaluación y seguridad. Sirve como apoyo para la defensa oral.

## Fallos habituales

- *No hay CSV*: descárgalo de Mendeley y cópialo a `data/raw`.
- *Múltiples CSV*: indica `--input "data/raw/archivo.csv"`.
- *No module named streamlit*: usa `py -3.14 -m pip install -r requirements.txt`.
- *Python 3.14 incompatible* tras instalar con otro `pip`: revisa `py -0p`; ejecuta pip **con `py -3.14 -m pip`**, no con pip global.
- *PowerShell no permite scripts*: no necesitas activar entornos; utiliza `py -3.14` desde VS Code.
- *Modelo no disponible*: debes completar `main.py todo` con datos oficiales, no basta ejecutar la interfaz.
