# Resultados medidos para el informe académico

**Datos reales de una ejecución del programa.**

- Archivo CSV: `Spaphish dataset - DiB.csv`
- SHA-256: `656b2245d58da72d640680e5c2a168673a130b38607f2a427c773bbb167e995e`
- Mensajes tras limpieza: 1395; entrenamiento: 1116; prueba reservada: 279.
- Modelo elegido según validación cruzada: **Regresión Logística**.
- F1 de phishing en validación cruzada: **0.9559**.
- F1 de phishing en test reservado: **0.9686**.
- Recall phishing en test: **0.9521**.
- Precisión phishing en test: **0.9858**.
- Accuracy en test: **0.9677**.
- ROC-AUC en test: **0.9965**.
- Brier score en test: **0.0259**.
- Falsos negativos: **7**; falsos positivos: **2**.

## Reglas de interpretación

Los resultados miden desempeño sobre una partición de correos del CSV aportado, no sobre WhatsApp, SMS, Nicaragua ni campañas nuevas.
Los umbrales bajo/medio/alto son provisionales y no una garantía de seguridad.
No usar cifras de pruebas sintéticas como resultados de SpaPhish.

## Evidencias

- `reports/metrics/resultados.json`
- `reports/metrics/comparacion_validacion.csv`
- `reports/figures/matriz_confusion.png`
- `reports/figures/curva_roc.png`
- `reports/figures/curva_precision_recall.png`
- `reports/metrics/analisis_errores_sin_texto.json`
