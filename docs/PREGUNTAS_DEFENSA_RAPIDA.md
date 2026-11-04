# EscudoIA — preguntas frecuentes del profesor

**¿Qué hace EscudoIA?** Recibe un texto en español y estima si presenta patrones de phishing, con una salida orientativa y recomendaciones. No verifica la identidad del remitente.

**¿De dónde provienen los datos?** SpaPhish v5 de Mendeley Data: la publicación documenta 1,395 correos, 731 phishing y 664 legítimos. Los registros retenidos tras limpieza pueden ser menos.

**¿Cuál es el método de IA?** Clasificación supervisada con representación TF-IDF y comparación de Naive Bayes Multinomial, Regresión Logística y SVM lineal.

**¿Qué metodología del proyecto utilizamos?** CRISP-DM: comprensión, comprensión de los datos, preparación, modelado, evaluación y despliegue.

**¿Por qué no basta con accuracy?** Porque importa detectar la clase phishing (recall) y controlar falsos positivos (precisión). El F1 resume ambas métricas.

**¿Cómo evitamos la fuga de datos?** Separando un test reservado por grupos de plantillas y ajustando el vocabulario TF-IDF dentro del Pipeline en cada pliegue de validación cruzada.

**¿Cómo sabemos qué modelo elegir?** El ganador se selecciona usando validación cruzada en entrenamiento, no el resultado del test. Luego se evalúa una vez sobre el test reservado.

**¿Qué sucede si se equivocó el modelo?** Se examinan falsos negativos y falsos positivos, se documentan las limitaciones y la interfaz recomienda verificar por otros medios.

**¿Por qué Python 3.14.5?** Es el intérprete instalado en el equipo; el proyecto emplea bibliotecas compatibles, no requiere cambiar de versión.

**¿Qué entregables verifican el proyecto?** Repositorio, cuatro notebooks, dataset local documentado, siete gráficos EDA, modelo `.joblib`, resultados JSON/CSV, aplicación Streamlit y pruebas automáticas.
