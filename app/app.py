"""Interfaz Streamlit del asistente: IA local y demostración educativa explícita."""
from __future__ import annotations

import json
import io
import subprocess
import zipfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st

from src.config import (ROOT, RAW, MODEL_FILE, METRICS, EDA, FIGURES, REPORTS,
                        SOURCE_URL, MODEL_META, ensure_dirs)
from src.models.predict_model import (analyze_message, educational_signals_only,
                                      load_metadata, load_model)

st.set_page_config(
    page_title="EscudoIA · Asistente contra estafas digitales",
    page_icon="🛡️", layout="wide", initial_sidebar_state="expanded",
)
ensure_dirs()
PUBLIC_MODE = (ROOT / "deployment_manifest.json").is_file()
st.markdown("""
<style>
.main .block-container { max-width: 1130px; padding-top: 1.7rem; }
.hero { background: linear-gradient(114deg,#102b55,#0d4a71 80%,#126b78); color: white;
        padding: 28px 32px; border-radius: 17px; margin-bottom: 22px; }
.hero h1 { font-size: 2.15rem; margin: 0 0 7px; color: white !important; }
.hero p { color: #d5e7f7; margin: 0; max-width: 730px; line-height: 1.55; }
.hint { border-left:4px solid #1d789d; background:#eef7fb; padding:12px 17px;
        border-radius: 4px 9px 9px 4px; color:#173955; }
.tiny-muted { color: #66788c; font-size: .88rem; }
@media(max-width: 720px) { .hero{padding:22px;} .hero h1{font-size:1.55rem;} }
</style>
""", unsafe_allow_html=True)


def show_hero(title: str, desc: str):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{desc}</p></div>', unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def cached_model(path: str, mod_time: int):
    # El modelo se carga exclusivamente desde el archivo entrenado local.
    return load_model(path)


def get_model():
    if not MODEL_FILE.exists():
        return None
    return cached_model(str(MODEL_FILE), MODEL_FILE.stat().st_mtime_ns)


def show_recommendations(items):
    for text in items:
        st.write("• " + text)


with st.sidebar:
    st.markdown("## 🛡️ EscudoIA")
    st.caption("Proyecto académico · UNI · Ingeniería de Sistemas")
    navigation = (["🔍 Analizar mensaje", "📊 Resultados y EDA", "🗂️ Datos del proyecto", "📘 Cómo funciona"]
                  if PUBLIC_MODE else
                  ["🔍 Analizar mensaje", "🧪 Entrenar IA", "📊 Resultados y EDA", "🗂️ Datos del proyecto", "📘 Cómo funciona", "✅ Preparar entrega"])
    section = st.radio("Navegación", navigation, label_visibility="collapsed")
    st.divider()
    if MODEL_FILE.exists():
        st.success("Modelo entrenado disponible")
        metadata = load_metadata()
        st.caption(f"Algoritmo: {metadata.get('modelo', 'modelo local')}")
    else:
        st.warning("Modelo pendiente de entrenamiento")
    st.caption("Predicción orientativa · no almacenamos mensajes analizados")
    if PUBLIC_MODE:
        st.caption("🌐 Versión pública para revisión académica")
    data_ready = bool(list(RAW.glob("*.csv")))
    result_ready = (METRICS / "resultados.json").exists()
    st.markdown("**Estado del proyecto**")
    st.caption(("✅" if data_ready else "⬜") + " Dataset disponible")
    st.caption(("✅" if MODEL_FILE.exists() else "⬜") + " Modelo entrenado")
    st.caption(("✅" if result_ready else "⬜") + " Métricas calculadas")
    st.markdown(f"[Dataset oficial SpaPhish v5]({SOURCE_URL})")

if section == "🔍 Analizar mensaje":
    show_hero("Asistente inteligente contra posibles estafas", "Analiza un texto en español, identifica patrones de phishing y recibe recomendaciones de seguridad. El resultado es orientativo, no una certificación de autenticidad.")
    st.info("**Privacidad:** no introduzcas contraseñas, códigos OTP, tarjetas ni información personal. No abrimos enlaces ni descargamos adjuntos.")
    col_a, col_b = st.columns([1.7, 1], gap="large")
    with col_a:
        sample = st.selectbox("Ejemplos de prueba (ficticios)", [
            "Escribir mi propio mensaje",
            "Alerta de cuenta suspendida",
            "Promesa de premio inesperado",
            "Mensaje cotidiano",
        ])
        examples = {
            "Alerta de cuenta suspendida": "URGENTE: su cuenta será suspendida hoy. Confirme su contraseña y el código de verificación en hxxps://portal[.]example.",
            "Promesa de premio inesperado": "Felicidades, ganó C$ 10,000 en un sorteo. Debe pagar una tarifa de activación para recibir el premio.",
            "Mensaje cotidiano": "Hola, la reunión de nuestro grupo quedó programada para mañana a las diez. Nos vemos en la universidad.",
        }
        selected = examples.get(sample, "")
        message = st.text_area(
            "Mensaje que quieres analizar", value=selected, height=195, max_chars=20000,
            placeholder="Pega aquí el mensaje sin datos personales...",
        )
        trained = MODEL_FILE.exists()
        label = "🛡️ Analizar con inteligencia artificial" if trained else "🔎 Examinar señales (demo sin IA)"
        if st.button(label, type="primary", use_container_width=True):
            try:
                result = analyze_message(message, model=get_model()) if trained else educational_signals_only(message)
                st.session_state["resultado"] = result
            except (ValueError, FileNotFoundError) as exc:
                st.session_state.pop("resultado", None)
                st.error(str(exc))
            except Exception as exc:
                st.session_state.pop("resultado", None)
                st.error("Ocurrió un error de inferencia. Revise la terminal del proyecto.")
        result = st.session_state.get("resultado")
        if result:
            st.divider()
            if "modo" in result:
                st.warning("**Demostración educativa:** reglas de detección transparentes. Aún NO es inteligencia artificial entrenada.")
            else:
                if result["etiqueta"] == 1:
                    st.error("**Clasificación del modelo: posible phishing**")
                else:
                    st.success("**Clasificación del modelo: sin suficientes indicios de phishing**")
                st.write("**Nivel orientativo:**", result["riesgo"])
                if result["puntaje_modelo"] is not None:
                    st.metric("Puntaje estimado por el modelo", f"{100*result['puntaje_modelo']:.1f}%")
                    st.progress(min(max(result["puntaje_modelo"], 0), 1))
                    st.caption("No es la probabilidad de que ocurra una estafa real. Las bandas de riesgo son provisionales.")
            st.markdown("#### Señales lingüísticas observables")
            if result["senales"]:
                show_recommendations(result["senales"])
            else:
                st.write("No se detectaron patrones de las reglas definidas. Esto **no** demuestra seguridad.")
            st.markdown("#### Recomendaciones de protección")
            show_recommendations(result["recomendaciones"])
            st.caption(result["advertencia"])
            st.download_button("⬇️ Guardar resultado (JSON, sin mensaje original)",
                data=json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name="resultado_escudoia.json", mime="application/json")
    with col_b:
        st.markdown("### ¿Qué analiza?")
        st.markdown("""
- Texto, palabras y frases de los mensajes.
- Posibles solicitudes de contraseñas y datos sensibles.
- Lenguaje de urgencia, premios o pagos.
- Presencia de URLs, sin abrirlas.
- Similitud con ejemplos etiquetados, **cuando hay un modelo entrenado**.
""")
        st.divider()
        st.markdown("### ¿Qué no puede confirmar?")
        st.markdown("""
- Identidad real del remitente.
- Si un sitio web es confiable.
- Si una cuenta efectivamente está bloqueada.
- Veracidad de amenazas, promociones o premios.
- Seguridad absoluta del mensaje.
""")
        if not MODEL_FILE.exists():
            st.warning("El modelo aún no está disponible. Para publicar esta aplicación, primero entrena con el CSV original y ejecuta `py -3.14 main.py publicar`.")

elif section == "🧪 Entrenar IA":
    show_hero("Laboratorio de entrenamiento", "Completa el proyecto desde esta misma aplicación: importar SpaPhish, generar 7 gráficos de EDA, entrenar 3 clasificadores, calcular métricas y guardar las evidencias del informe.")
    st.info("**Importante:** utiliza el CSV original de SpaPhish v5. Las cifras del informe solo serán válidas después de ejecutar el entrenamiento con ese archivo; no se incluyen resultados inventados.")
    st.markdown("### 1. Verificar el archivo de datos")
    csv_files = sorted(RAW.glob("*.csv"))
    if not csv_files:
        st.error("No se encontró ningún CSV en `data/raw/`. Descárgalo del enlace oficial y súbelo a continuación.")
        st.markdown(f"[⬇️ Abrir SpaPhish v5 en Mendeley Data]({SOURCE_URL})")
        if st.button("🌐 Intentar descargar CSV automáticamente desde Mendeley"):
            from src.data.download_official import download_spaphish
            with st.spinner("Consultando la API pública del dataset..."):
                try:
                    downloaded = download_spaphish()
                except (RuntimeError, FileExistsError, ValueError) as error:
                    st.warning(str(error))
                    st.info("Si la descarga automática falla, utiliza el botón de carga manual que aparece debajo.")
                else:
                    st.success(f"Datos oficiales descargados: {downloaded.name}")
                    st.rerun()
        source_csv = st.file_uploader("Selecciona el archivo CSV de SpaPhish", type=["csv"], key="training_upload")
        if source_csv is not None and st.button("Guardar CSV para entrenamiento", type="primary"):
            safe_name = Path(source_csv.name).name
            output_csv = RAW / safe_name
            if output_csv.exists():
                st.warning("El archivo ya existe en data/raw; no se sobrescribió.")
            else:
                output_csv.write_bytes(source_csv.getbuffer())
                st.success(f"Archivo guardado: {output_csv.name}")
                st.rerun()
    else:
        selected_file = st.selectbox("Archivo seleccionado", csv_files, format_func=lambda x: x.name)
        st.success(f"CSV listo: `{selected_file.name}` ({selected_file.stat().st_size / 1048576:.2f} MB)")
        if len(csv_files) > 1:
            st.warning("Hay varios CSV en data/raw: comprueba que elegiste el archivo oficial.")
        st.markdown("### 2. Elegir la modalidad")
        modo = st.radio("Búsqueda de hiperparámetros", ["Rápida (3 pliegues de validación)", "Completa (5 pliegues de validación)"], horizontal=True)
        quick = modo.startswith("Rápida")
        st.caption("Las dos modalidades usan scikit-learn, TF-IDF, Naive Bayes, Regresión Logística y SVM, deduplicación, prueba reservada y calibración. El modo completo ajusta más combinaciones; el rápido facilita ensayar el flujo antes de la entrega.")
        if st.button("🚀 Preparar datos, generar EDA y entrenar modelos", type="primary", use_container_width=True):
            cmd = [sys.executable, str(ROOT / "main.py"), "todo", "--input", str(selected_file)]
            if quick:
                cmd.append("--rapido")
            with st.spinner("Procesando datos, comparando algoritmos y generando el reporte. Observa el resultado al finalizar..."):
                try:
                    process = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
                except subprocess.TimeoutExpired:
                    st.error("La ejecución excedió el tiempo límite de 30 minutos. Puedes continuar desde la terminal de VS Code: `py -3.14 main.py todo`.")
                    process = None
                except OSError as error:
                    st.error(f"No se pudo ejecutar el entrenamiento: {error}")
                    process = None
            if process is not None:
                logtext = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
                with st.expander("Registro completo del entrenamiento", expanded=process.returncode != 0):
                    st.code(logtext[-25000:] or "Sin registro disponible", language="text")
                if process.returncode == 0 and MODEL_FILE.exists() and (METRICS / "resultados.json").exists():
                    st.success("✅ Entrenamiento terminado: se generaron el modelo, las métricas y los gráficos reales del archivo proporcionado.")
                    st.balloons()
                    st.info("Abre **Resultados y EDA** para comprobar las cifras y descargar las evidencias. Si deseas ver el estado actualizado en el menú lateral, cambia de página o recarga.")
                else:
                    st.error("El entrenamiento no terminó correctamente. Abre el registro anterior y comprueba el CSV y sus columnas.")
    st.divider()
    st.markdown("### 3. Comprobar resultados")
    if MODEL_FILE.exists() and (METRICS / "resultados.json").exists():
        st.success("Modelo guardado y métricas disponibles. ¡Ya puedes utilizar el clasificador de IA!")
        if st.button("📊 Ir a los resultados", use_container_width=True):
            st.info("Selecciona **Resultados y EDA** en la barra lateral.")
    else:
        st.warning("Todavía no hay resultados de entrenamiento. Antes de entrenar, el analizador únicamente muestra una demostración de reglas.")
    st.caption("Alternativa desde la terminal de Visual Studio Code: `py -3.14 main.py todo --rapido` o `py -3.14 main.py todo`.")

elif section == "📊 Resultados y EDA":
    show_hero("Panel de investigación", "Métricas y gráficos generados por la ejecución real del pipeline de entrenamiento. No se muestran porcentajes inventados.")
    path = METRICS / "resultados.json"
    if not path.exists():
        st.warning("Todavía no existen métricas de evaluación. Ejecuta `python -m src.models.train_model` desde Visual Studio Code.")
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        winner = data["modelo_seleccionado_por_cv"]
        st.write("**Modelo seleccionado mediante validación cruzada:**", winner)
        m = data["test_final"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{m['accuracy']:.1%}")
        c2.metric("Precisión phishing", f"{m['precision_phishing']:.1%}")
        c3.metric("Recall phishing", f"{m['recall_phishing']:.1%}")
        c4.metric("F1 phishing", f"{m['f1_phishing']:.1%}")
        t1, t2 = st.columns(2)
        if "roc_auc" in m:
            t1.metric("ROC-AUC", f"{m['roc_auc']:.3f}")
        if "brier_score" in m:
            t2.metric("Brier (menor es mejor)", f"{m['brier_score']:.3f}")
        st.caption("Métricas sobre el test reservado del archivo local; no extrapolables automáticamente a WhatsApp o Nicaragua.")
        st.markdown("#### Interpretación de los errores")
        err1, err2 = st.columns(2)
        err1.metric("Falsos negativos", m["FN"], help="Mensajes de phishing que el modelo no detectó")
        err2.metric("Falsos positivos", m["FP"], help="Mensajes legítimos señalados erróneamente como phishing")
        if m["FN"]:
            st.warning("Hay mensajes de phishing no detectados. Se recomienda inspeccionar causas y mejorar la generalización antes de un uso real.")
        table = pd.DataFrame.from_dict(data["comparacion_validacion"], orient="index")
        cols = ["accuracy_cv", "f1_cv", "precision_cv", "recall_cv", "desviacion_f1_cv", "duracion_segundos"]
        st.markdown("### Comparación entre modelos (validación cruzada)")
        st.dataframe(table[cols].rename_axis("Modelo"), use_container_width=True)
        st.info("La elección se hizo con validación cruzada sobre el entrenamiento; la prueba se reservó para evaluar una sola vez al ganador. Las métricas de esta tabla son de CV, no del test.")
        error_path = METRICS / "analisis_errores_sin_texto.json"
        if error_path.exists():
            with st.expander("Análisis agregado de errores, sin mostrar el texto"):
                st.json(json.loads(error_path.read_text(encoding="utf-8")), expanded=False)
        a, b = st.columns(2)
        for column, name in [(a, "matriz_confusion.png"), (b, "curva_roc.png")]:
            picture = FIGURES / name
            if picture.exists():
                column.image(str(picture), use_container_width=True)
        p = FIGURES / "curva_precision_recall.png"
        if p.exists():
            st.image(str(p), width=560)
        st.download_button("Descargar métricas medidas (JSON)", path.read_bytes(), "resultados_ia.json", "application/json")
        terms_path = METRICS / "terminos_globales.json"
        if terms_path.exists():
            terms = json.loads(terms_path.read_text(encoding="utf-8"))
            with st.expander("Términos globales asociados con cada clase"):
                a1, a2 = st.columns(2)
                a1.markdown("**Términos asociados con phishing**")
                for t in terms.get("phishing", [])[:10]:
                    a1.write("• " + t["termino"])
                a2.markdown("**Términos asociados con comunicaciones legítimas**")
                for t in terms.get("legitimo", [])[:10]:
                    a2.write("• " + t["termino"])
                st.caption("Asociaciones estadísticas globales; no establecen causa ni explican necesariamente una predicción individual.")
    st.divider()
    st.markdown("### Análisis exploratorio de datos")
    found = False
    for file in ["01_distribucion_clases.png", "02_longitud_palabras.png", "03_indicadores_por_clase.png", "04_boxplot_longitud.png", "05_valores_ausentes.png", "06_enlaces_por_clase.png", "07_terminos_phishing.png"]:
        img = EDA / file
        if img.exists():
            st.image(str(img), use_container_width=True)
            found = True
    if not found:
        st.info("EDA pendiente: abre **Entrenar IA** y pulsa el botón de preparación y entrenamiento.")
    else:
        eda_summary = EDA / "eda_resumen.json"
        if eda_summary.exists():
            with st.expander("Resumen estadístico de los datos analizados"):
                st.json(json.loads(eda_summary.read_text(encoding="utf-8")), expanded=False)

elif section == "🗂️ Datos del proyecto":
    show_hero("Fuente de datos y preparación", "El modelo se entrena con correos electrónicos etiquetados, no con mensajes personales de los usuarios de la interfaz.")
    st.markdown("### SpaPhish v5 — fuente oficial")
    st.markdown(f"[Abrir página de descarga de Mendeley Data]({SOURCE_URL})")
    st.write("El corpus publicado contiene **1.395 correos** en español: 731 phishing y 664 legítimos, según los autores. La cifra efectiva de entrenamiento puede disminuir tras limpieza y deduplicación.")
    st.caption("CSV oficial con separador punto y coma. La etiqueta 0 corresponde a legítimo y la 1 a phishing.")
    csv_files = sorted(RAW.glob("*.csv"))
    if PUBLIC_MODE:
        st.info("Esta versión publicada no incluye el texto original del dataset ni permite subir datos. El modelo y las evidencias fueron preparados previamente en Visual Studio Code.")
    else:
        if csv_files:
            st.success("CSV presentes en data/raw/: " + ", ".join(path.name for path in csv_files))
        else:
            st.warning("Aún no hay un CSV en data/raw/. Descarga primero el archivo desde Mendeley Data.")
        st.markdown("### Colocar un CSV oficial en la carpeta del proyecto")
        uploaded = st.file_uploader("Selecciona SOLO el dataset oficial anonimizado (no mensajes privados)", type=["csv"])
        if uploaded is not None:
            if st.button("Guardar archivo en data/raw/", type="primary"):
                target = RAW / Path(uploaded.name).name
                if target.exists():
                    st.error("Ya existe un archivo con ese nombre; elimínalo manualmente si deseas reemplazarlo.")
                else:
                    target.write_bytes(uploaded.getbuffer())
                    st.success(f"Dataset guardado: data/raw/{target.name}. Ahora ejecuta los comandos de EDA y entrenamiento en VS Code.")
    audit = METRICS / "auditoria_dataset.json"
    if audit.exists():
        st.markdown("### Auditoría del dataset")
        st.json(json.loads(audit.read_text(encoding="utf-8")), expanded=False)
    if not PUBLIC_MODE:
        st.markdown("Puedes hacer todo desde **Entrenar IA**, en el menú izquierdo. Alternativamente, en VS Code ejecuta:")
        st.code("py -3.14 main.py todo --rapido\n# Para el protocolo académico completo:\npy -3.14 main.py todo", language="powershell")

elif section == "✅ Preparar entrega":
    show_hero("Preparar la entrega del curso", "Comprueba qué evidencias están listas y descarga un paquete con los resultados del modelo, las estadísticas y los gráficos, sin incluir textos del dataset ni mensajes privados.")
    checkpoints = [
        ("CSV del dataset en data/raw/", bool(list(RAW.glob("*.csv"))), "Sube SpaPhish desde Datos del proyecto o Entrenar IA"),
        ("Auditoría y limpieza de datos", (METRICS / "auditoria_dataset.json").exists(), "Ejecuta preparación de datos"),
        ("Análisis exploratorio con figuras", (EDA / "eda_resumen.json").exists(), "Ejecuta EDA"),
        ("Modelo de IA entrenado", MODEL_FILE.exists(), "Entrena los tres algoritmos"),
        ("Métricas y matriz de confusión", (METRICS / "resultados.json").exists() and (FIGURES / "matriz_confusion.png").exists(), "Ejecuta evaluación"),
        ("Resumen académico para el informe", (REPORTS / "RESUMEN_REAL_PARA_INFORME.md").exists(), "Entrena el modelo para generar el reporte"),
    ]
    for label, ready, pending in checkpoints:
        st.write(("✅ " if ready else "⬜ ") + "**" + label + "**" + ("" if ready else f" — {pending}"))
    completed = sum(status for _, status, _ in checkpoints)
    st.progress(completed / len(checkpoints))
    st.caption(f"Evidencias generadas: {completed} de {len(checkpoints)}. Los resultados dependen del CSV realmente ejecutado.")
    st.markdown("### Evidencias para entregar")
    if completed >= 5:
        buff = io.BytesIO()
        with zipfile.ZipFile(buff, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for folder in [REPORTS / "metrics", REPORTS / "eda", REPORTS / "figures"]:
                if folder.exists():
                    for file in sorted(folder.rglob("*")):
                        if file.is_file() and file.suffix.lower() in {".json", ".csv", ".txt", ".png"}:
                            zf.write(file, file.relative_to(ROOT).as_posix())
            summary = REPORTS / "RESUMEN_REAL_PARA_INFORME.md"
            if summary.exists():
                zf.write(summary, summary.relative_to(ROOT).as_posix())
        st.download_button("⬇️ Descargar evidencias reales (ZIP)", data=buff.getvalue(), file_name="ESCUDOIA_EVIDENCIAS_PARA_INFORME.zip", mime="application/zip", use_container_width=True)
        st.success("Esta descarga contiene cifras y gráficos medidos; adjúntalos como evidencia del informe, indicando el archivo CSV utilizado.")
    else:
        st.info("El ZIP de evidencias aparecerá cuando se genere el modelo y las métricas. Empieza por **Entrenar IA**.")
    st.markdown("### Comprobaciones técnicas")
    st.code("py -3.14 main.py pruebas\npy -3.14 main.py estado", language="powershell")
    st.markdown("### Publicar para el profesor mediante GitHub")
    st.info("Cuando termines con SpaPhish, abre una nueva terminal en VS Code y ejecuta: `py -3.14 main.py verificar` y `py -3.14 main.py publicar`. Ese comando genera una carpeta y un ZIP específicos para GitHub **incluyendo el modelo y las métricas**; el ZIP de evidencias de arriba, por sí solo, no publica la aplicación.")
    st.markdown("Lee `docs/PUBLICAR_GITHUB_STREAMLIT.md`. El modelo debe quedar en `models/modelo_estafas_v1.joblib` en GitHub.")
    st.markdown("### Qué mostrar durante la exposición")
    st.markdown("1. **Datos:** archivo oficial, clases y limpieza.\n2. **EDA:** siete gráficos y hallazgos relevantes.\n3. **Modelado:** tres algoritmos, TF-IDF, validación cruzada.\n4. **Evaluación:** F1, recall, precisión, accuracy y matriz de confusión.\n5. **Demostración:** analizar un ejemplo de phishing y un mensaje cotidiano.\n6. **Limitaciones:** no certifica identidad ni seguridad y puede fallar con SMS/WhatsApp.")

else:
    show_hero("Metodología y transparencia", "Sistema construido conforme a los capítulos 8–16 del informe de curso: NLP, clasificación supervisada, CRISP-DM, evaluación y consideraciones éticas.")
    st.markdown("""
### Proceso CRISP-DM
1. Comprensión del problema: asistir al usuario sin emitir una sentencia de fraude.
2. Comprensión de datos: analizar SpaPhish y sus etiquetas.
3. Preparación: limpieza y deduplicación; evitar que una misma plantilla aparezca en entrenamiento y prueba.
4. Modelado: TF-IDF, Naive Bayes Multinomial, Regresión Logística y SVM lineal.
5. Evaluación: precisión, recall, F1, matriz de confusión y ROC/PR.
6. Despliegue: Streamlit, procesamiento local y advertencias interpretables.

### Interpretación responsable
La clasificación **legítimo** no significa que el mensaje sea seguro. Un mensaje con lenguaje urgente también puede ser legítimo. Las señales transparentes de la interfaz son heurísticas descriptivas, no pruebas de delito.

### Arquitectura
`CSV SpaPhish → Validación/deduplicación → TF-IDF + 3 clasificadores → Selección por CV → Test reservado → Modelo local → Interfaz`

### Protección de datos
La aplicación no guarda por defecto los mensajes copiados por los usuarios ni navega hacia los enlaces encontrados. Solo se escribe un archivo al seleccionar explícitamente subir el CSV. No cargues modelos joblib de fuentes desconocidas.
""")
    st.markdown(f"**Referencia:** [SpaPhish v5]({SOURCE_URL}).")
