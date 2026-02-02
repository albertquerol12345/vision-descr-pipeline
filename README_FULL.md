# Vision Description Pipeline

Pipeline ligero para generar descripciones consistentes (80-100 palabras) de creatividades de moda/joyería usando la API de visión de OpenAI y consolidar todo en un CSV maestro.

## Estructura

```
vision_descr_pipeline/
├── config.toml               # rutas y parámetros principales
├── .env.example              # plantilla para OPENAI_API_KEY
├── data/
│   ├── creatives_input.csv   # CSV de entrada con metadatos (lo pones tú)
│   └── creatives_master.csv  # CSV de salida enriquecido
├── images/                   # carpeta raíz con las imágenes
├── logs/
├── src/
│   ├── __init__.py
│   ├── describe_images.py    # lógica de llamadas a la API y enriquecido CSV
│   └── main.py               # CLI (describe-all, resume-stats)
└── requirements.txt
```

## Instalación

```bash
cd ~/vision_descr_pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

1. Copia `.env.example` a `.env` y añade tu clave:
   ```bash
   cp .env.example .env
   echo "OPENAI_API_KEY=sk-..." >> .env
   ```
2. Edita `config.toml` para apuntar a tus rutas (carpeta de imágenes, CSV de entrada/salida, modelo, nº palabras, etc.).
3. Crea / coloca `data/creatives_input.csv` con columnas mínimas:
   - `image_id`
   - `image_path`
   - `source`
   - (opcional) `product_id`, `likes`, `comments_count`, ...

## Uso

### 1. Generar descripciones

```bash
source .venv/bin/activate
python -m src.main describe-all
```

Esto:
- Lee `config.toml`.
- Carga `data/creatives_input.csv`.
- Llama a la API de visión para cada imagen sin `description_es`.
- Va escribiendo/actualizando `data/creatives_master.csv` tras cada lote.
- Reintenta automáticamente en caso de errores de red (hasta el límite configurado).
- Al final muestra estadísticas (procesadas, saltadas, palabras aproximadas, tokens estimados).

### 2. Resumen rápido

```bash
python -m src.main resume-stats
```

Muestra nº de filas, cuántas ya tienen descripción y la media de palabras/tokens.

## Estimación de coste/tokens (documental)

- Objetivo por imagen: 80-100 palabras ≈ 60-80 tokens de salida (0.75 tokens/palabra).
- Para 400 imágenes ⇒ ~24k-32k tokens de salida.
- Modelos “mini” de OpenAI cuestan del orden de 0.15 $/1M tokens de salida ⇒ < 0.005 $ en salida.
- Entrada (prompts + imagen) añade unos céntimos más, por lo que describir 400 imágenes debería costar **unos pocos céntimos** en total.

## Notas

- El script respeta filas ya descritas (`description_es` no vacía) para poder reanudar.
- Guardamos logs en `logs/describe.log` (rotación simple).
- Ajusta `target_min_words` / `target_max_words` en el config para cambiar el tamaño del texto.
- `creatives_master.csv` conserva todas las columnas originales más `description_es` y metadatos adicionales (`words_count`, `runtime_ms`).
