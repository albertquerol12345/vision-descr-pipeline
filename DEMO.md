# Vision Pipeline — Demo Guide

Pipeline CLI para generar descripciones de imágenes y enriquecer un CSV.

---

## ✅ Demo incluida (real)

El repo incluye **2 imágenes**:
- `images/sample_001.png`
- `images/sample_002.png`

Y un CSV de entrada:
- `data/creatives_input.csv`

---

## 🚀 Ejecutar demo

```bash
git clone https://github.com/albertquerol12345/vision-descr-pipeline.git
cd vision-descr-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Añade tu OPENAI_API_KEY

python -m src.main describe-all
```

---

## 📄 Output esperado

Se genera/actualiza:
- `data/creatives_master.csv`
- `logs/describe.log`

También hay un ejemplo:
- `data/creatives_output_sample.csv`

---

## 🔁 Reanudar y resumen

```bash
python -m src.main resume-stats
```

---

## 📌 Notas

- La longitud objetivo es configurable en `config.toml`.
- El coste depende del modelo y del número de imágenes.
