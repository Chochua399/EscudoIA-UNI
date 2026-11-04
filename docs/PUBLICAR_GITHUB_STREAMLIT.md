# Publicar EscudoIA para que lo revise el docente

## 1. Terminar entrenamiento en Visual Studio Code (Windows, Python 3.14)

Este proyecto **no** publica métricas ficticias. Necesitas el CSV original de **SpaPhish v5** publicado en Mendeley Data, DOI: https://doi.org/10.17632/hz2d6gz7pc.5

1. Abre la carpeta `ESCUDOIA_COMPLETO_PYTHON_3_14_5` en VS Code (debe verse `main.py`).
2. Descarga `Spaphish dataset - DiB.csv` desde la página oficial y colócalo en `data/raw/` o súbelo desde **Entrenar IA**.
3. En la terminal:

```powershell
py -3.14 main.py todo
```

No añadas `--rapido` a la ejecución definitiva: la guía del docente exige cinco pliegues de validación.

4. Comprueba que existen `reports/metrics/resultados.json`, las figuras en `reports/eda/` y el modelo en `models/`.
5. Comprueba la publicación:

```powershell
py -3.14 main.py verificar
py -3.14 main.py publicar
```

El comando `publicar` genera:

- **`ESCUDOIA_LISTO_PARA_GITHUB/`**: proyecto completo para subir a GitHub.
- **`ESCUDOIA_LISTO_PARA_GITHUB.zip`**: copia comprimida de ese proyecto.

Esta carpeta incluye modelo `joblib`, métricas y gráficos; excluye CSV original, entorno virtual y mensajes de usuarios. **Sube los archivos que están DENTRO de `ESCUDOIA_LISTO_PARA_GITHUB`, no la carpeta original de desarrollo**, para no omitir el modelo por reglas de `.gitignore`.

## 2. Crear repositorio en GitHub

1. En https://github.com, selecciona **New repository**.
2. Nombre sugerido: `escudoia-uni`.
3. Elige **Public** si lo pide el profesor; revisa primero que el paquete contenga únicamente datos académicos publicables.
4. Sin crear otro README si ya vas a subir el existente.
5. Abre **Add file → Upload files** y arrastra **todo el contenido** de `ESCUDOIA_LISTO_PARA_GITHUB/` a la raíz del repositorio. Si GitHub no conserva las carpetas al seleccionar archivos, arrastra la carpeta completa desde el Explorador de Windows.
6. Haz clic en **Commit changes**. Confirma en GitHub que aparecen `app/app.py`, `src`, `models/modelo_estafas_v1.joblib`, `reports/metrics/resultados.json`, `requirements.txt` y `deployment_manifest.json`.

**Advertencia:** GitHub puede advertir si el modelo supera el límite permitido para cargas mediante navegador. Si eso ocurre, usa Git/Git LFS o reduce el artefacto antes de publicar, sin borrar el modelo de la web.

## 3. Crear el enlace público de Streamlit

1. Entra en https://share.streamlit.io con GitHub.
2. **Create app** y selecciona el repositorio, rama `main` y ruta **`app/app.py`**.
3. En **Advanced settings**, selecciona Python **3.14** (la misma versión principal en que entrenaste).
4. Pulsa **Deploy**. Si el servicio muestra un error, revisa **Manage app → Logs**.
5. Verifica desde una ventana de incógnito que **Analizar mensaje** realmente usa IA, **Resultados y EDA** enseña métricas y gráficos, y **Datos del proyecto** muestra la fuente. La edición publicada no permite reentrenar ni cargar datos privados.

## 4. Evidencias que mostrarás al docente

- Enlace del repositorio GitHub.
- Enlace público `*.streamlit.app`.
- Captura de la predicción de dos mensajes **ficticios** distintos.
- Captura de comparación de los tres modelos y métricas del test.
- Captura de las siete figuras de EDA o del panel donde se muestran.
- Archivo `reports/RESUMEN_REAL_PARA_INFORME.md` con las cifras obtenidas.
- Documento Word final: sustituye las secciones de resultados pendientes con estas cifras reales.

## Alcance y límites

El sistema fue diseñado para mensajes en español, pero entrenado originalmente con **correos electrónicos** de SpaPhish. No verifica enlaces ni remitentes. Las predicciones no garantizan la seguridad de mensajes de WhatsApp/SMS ni sustituyen medidas profesionales. El modelo es académico y la calidad de resultados depende de los datos analizados.
