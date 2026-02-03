# Vision Description Pipeline

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![OpenAI](https://img.shields.io/badge/API-OpenAI%20Vision-green.svg)
![Resumable](https://img.shields.io/badge/feature-resumable-orange.svg)

**CLI para enriquecer catálogos de imágenes con descripciones en español**

Genera descripciones consistentes (longitud objetivo configurable) y actualiza un CSV maestro. Procesamiento reanudable y logs básicos.

![Demo Preview](assets/preview.gif)

---

## ⚡ Quick Start

```bash
git clone https://github.com/albertquerol12345/vision-descr-pipeline.git
cd vision-descr-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configurar API
cp .env.example .env
# Edita .env y añade: OPENAI_API_KEY=sk-...

# Ejecutar
python -m src.main describe-all
```

---

## 🎯 Qué hace

**Entrada:** `data/creatives_input.csv` con `image_id` y `image_path`  
**Salida:** `data/creatives_master.csv` con `description_es`, conteo de palabras y metadatos

Características verificables:
- **Reanudable** (`save_every = 5` en `config.toml`)
- **Idempotente** (no re-procesa filas ya descritas)
- **Logs** en `logs/describe.log`

---

## 📦 Demo incluida (real)

El repo incluye **2 imágenes de demo**:
- `images/sample_001.png`
- `images/sample_002.png`

Y un CSV de entrada:
- `data/creatives_input.csv`

Salida de ejemplo:
- `data/creatives_output_sample.csv`

---

## 🧩 Configuración (config.toml)

```toml
[paths]
images_root = "./images"
input_csv = "./data/creatives_input.csv"
output_csv = "./data/creatives_master.csv"
log_file = "./logs/describe.log"

[openai]
model = "gpt-4o-mini"
max_retries = 5
retry_delay_seconds = 5

[target]
min_words = 80
max_words = 100

[batch]
save_every = 5
```

> **Nota:** la longitud objetivo es configurable y puede variar en función del prompt y el modelo.

---

## 🧪 CLI útil

```bash
# Generar descripciones
python -m src.main describe-all

# Ver resumen del CSV maestro
python -m src.main resume-stats
```

---

## 📊 Costes

El coste depende del modelo y del número de imágenes. Para estimar tokens y palabras:

```bash
python -m src.main resume-stats
```

---

## 📁 Estructura

```
vision-descr-pipeline/
├── config.toml
├── data/
│   ├── creatives_input.csv
│   └── creatives_master.csv
├── images/
├── src/
└── logs/
```

---

## 📚 Documentación

- [DEMO.md](DEMO.md) — guía paso a paso
- [data/creatives_output_sample.csv](data/creatives_output_sample.csv) — output demo
- [config.toml](config.toml) — configuración completa

---

## 🛠️ Tech Stack

**API:** OpenAI Vision  
**Data:** Pandas · CSV · TOML  
**CLI:** argparse
