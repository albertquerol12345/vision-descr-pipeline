from __future__ import annotations

import base64
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - compat 3.10
    import tomli as tomllib  # type: ignore[no-redef]
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LOGGER = logging.getLogger("vision_descr")


@dataclass
class AppConfig:
    images_root: Path
    input_csv: Path
    output_csv: Path
    log_file: Path
    model: str
    max_retries: int
    retry_delay: int
    target_min_words: int
    target_max_words: int
    save_every: int


PROMPT_TEMPLATE = (
    "Eres un asistente experto en análisis visual para e-commerce de moda y joyería. "
    "Describe esta imagen en {min_words}-{max_words} palabras en español, de forma objetiva y concreta, "
    "incluyendo: tipo de plano, entorno, estilo/mood, productos visibles, colores dominantes, presencia de modelo y elementos relevantes. "
    "No inventes métricas ni contenido que no esté en la imagen."
)


def load_config(config_path: Path | None = None) -> AppConfig:
    path = config_path or Path(__file__).resolve().parents[1] / "config.toml"
    with path.open("rb") as fh:
        raw = tomllib.load(fh)

    paths_cfg: Dict[str, Any] = raw.get("paths", {})
    openai_cfg: Dict[str, Any] = raw.get("openai", {})
    target_cfg: Dict[str, Any] = raw.get("target", {})
    batch_cfg: Dict[str, Any] = raw.get("batch", {})

    base_dir = path.parent

    def resolve(value: str, default: str) -> Path:
        candidate = Path(value or default)
        if not candidate.is_absolute():
            candidate = (base_dir / candidate).resolve()
        return candidate

    images_root = resolve(paths_cfg.get("images_root", "./images"), "./images")
    input_csv = resolve(paths_cfg.get("input_csv", "./data/creatives_input.csv"), "./data/creatives_input.csv")
    output_csv = resolve(paths_cfg.get("output_csv", "./data/creatives_master.csv"), "./data/creatives_master.csv")
    log_file = resolve(paths_cfg.get("log_file", "./logs/describe.log"), "./logs/describe.log")

    return AppConfig(
        images_root=images_root,
        input_csv=input_csv,
        output_csv=output_csv,
        log_file=log_file,
        model=openai_cfg.get("model", "gpt-4o-mini"),
        max_retries=int(openai_cfg.get("max_retries", 5)),
        retry_delay=int(openai_cfg.get("retry_delay_seconds", 5)),
        target_min_words=int(target_cfg.get("min_words", 80)),
        target_max_words=int(target_cfg.get("max_words", 100)),
        save_every=int(batch_cfg.get("save_every", 5)),
    )


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def load_dataset(cfg: AppConfig) -> pd.DataFrame:
    if not cfg.input_csv.exists():
        raise FileNotFoundError(f"No se encontró el CSV de entrada: {cfg.input_csv}")

    base_df = pd.read_csv(cfg.input_csv)
    if "image_id" not in base_df.columns:
        raise ValueError("La columna 'image_id' es obligatoria en creatives_input.csv")

    if cfg.output_csv.exists():
        master_df = pd.read_csv(cfg.output_csv)
        if "image_id" in master_df.columns:
            master_df = master_df.set_index("image_id")
            base_df = base_df.set_index("image_id")
            for col in master_df.columns:
                if col not in base_df.columns:
                    base_df[col] = master_df[col]
            overlap_cols = [col for col in master_df.columns if col in base_df.columns]
            base_df.loc[master_df.index, overlap_cols] = master_df[overlap_cols]
            base_df = base_df.reset_index()
        else:
            LOGGER.warning("El CSV maestro existente no tiene columna image_id; se ignorará para merge.")
    if "description_es" not in base_df.columns:
        base_df["description_es"] = ""
    if "description_es_words" not in base_df.columns:
        base_df["description_es_words"] = pd.NA
    if "description_es_tokens_est" not in base_df.columns:
        base_df["description_es_tokens_est"] = pd.NA
    if "description_last_updated" not in base_df.columns:
        base_df["description_last_updated"] = pd.NA
    return base_df


def _encode_image(image_path: Path) -> str:
    with image_path.open("rb") as fh:
        data = fh.read()
    b64 = base64.b64encode(data).decode("utf-8")
    mime = _guess_mime(image_path)
    return f"{mime};base64,{b64}"


def _guess_mime(image_path: Path) -> str:
    ext = image_path.suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        return "data:image/jpeg"
    if ext == ".png":
        return "data:image/png"
    if ext == ".webp":
        return "data:image/webp"
    if ext == ".gif":
        return "data:image/gif"
    return "data:image/png"


def _extract_text(response: Any) -> str:
    text_chunks: List[str] = []
    try:
        for block in getattr(response, "output", []) or []:
            contents = getattr(block, "content", []) or []
            for content in contents:
                ctype = getattr(content, "type", None) or (content.get("type") if isinstance(content, dict) else None)
                if ctype == "output_text":
                    text = getattr(content, "text", None) or (content.get("text") if isinstance(content, dict) else None)
                    if text:
                        text_chunks.append(text)
    except AttributeError:
        pass
    if not text_chunks and hasattr(response, "output_text"):
        text_chunks.append(response.output_text)
    return " ".join(text_chunks).strip()


def describe_images(cfg: AppConfig) -> Tuple[int, int, int, int]:
    df = load_dataset(cfg)
    client = OpenAI()
    processed = skipped = total_words = total_tokens = 0

    for idx, row in df.iterrows():
        existing_value = row.get("description_es", "")
        if pd.notna(existing_value) and str(existing_value).strip():
            skipped += 1
            continue
        image_path = Path(str(row.get("image_path", "")))
        if not image_path.is_absolute():
            image_path = cfg.images_root / image_path
        if not image_path.exists():
            LOGGER.warning("Imagen no encontrada: %s", image_path)
            continue

        prompt = PROMPT_TEMPLATE.format(
            min_words=cfg.target_min_words,
            max_words=cfg.target_max_words,
        )
        image_data_url = _encode_image(image_path)
        description = _call_openai(
            client=client,
            model=cfg.model,
            prompt=prompt,
            image_data_url=image_data_url,
            max_retries=cfg.max_retries,
            retry_delay=cfg.retry_delay,
        )
        if not description:
            LOGGER.warning("No se obtuvo descripción para %s", image_path)
            continue
        words = _count_words(description)
        tokens = int(words * 1.3)
        timestamp = pd.Timestamp.utcnow().isoformat()

        df.at[idx, "description_es"] = description
        df.at[idx, "description_es_words"] = words
        df.at[idx, "description_es_tokens_est"] = tokens
        df.at[idx, "description_last_updated"] = timestamp

        processed += 1
        total_words += words
        total_tokens += tokens

        if processed % max(cfg.save_every, 1) == 0:
            _save_output(df, cfg.output_csv)
            LOGGER.info("Guardado intermedio tras %s descripciones", processed)

    _save_output(df, cfg.output_csv)
    return processed, skipped, total_words, total_tokens


def _save_output(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def _count_words(text: str) -> int:
    if not text:
        return 0
    return len([word for word in text.split() if word.strip()])


def _call_openai(
    *,
    client: OpenAI,
    model: str,
    prompt: str,
    image_data_url: str,
    max_retries: int,
    retry_delay: int,
) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            request_kwargs: Dict[str, Any] = {}
            if "nano" not in model.lower():
                request_kwargs["temperature"] = 0.4
            response = client.responses.create(
                model=model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_image", "image_url": image_data_url},
                        ],
                    }
                ],
                max_output_tokens=220,
                **request_kwargs,
            )
            text = _extract_text(response)
            if text:
                return text
            last_error = RuntimeError("Respuesta sin contenido")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            LOGGER.warning("Error en llamada a OpenAI (intento %s/%s): %s", attempt, max_retries, exc)
        time.sleep(retry_delay)
    if last_error:
        LOGGER.error("Fallo tras %s intentos: %s", max_retries, last_error)
    return ""


def resume_stats(cfg: AppConfig) -> Dict[str, Any]:
    if not cfg.output_csv.exists():
        raise FileNotFoundError("Aún no existe creatives_master.csv; ejecuta describe-all primero.")
    df = pd.read_csv(cfg.output_csv)
    total = len(df)
    with_desc = df["description_es"].astype(str).str.strip().astype(bool).sum()
    words_total = df.get("description_es_words", pd.Series([0] * total)).fillna(0).astype(int).sum()
    tokens_total = df.get("description_es_tokens_est", pd.Series([0] * total)).fillna(0).astype(int).sum()
    avg_words = words_total / with_desc if with_desc else 0
    avg_tokens = tokens_total / with_desc if with_desc else 0
    return {
        "total_rows": int(total),
        "with_description": int(with_desc),
        "words_total": int(words_total),
        "tokens_total": int(tokens_total),
        "avg_words": round(avg_words, 2),
        "avg_tokens": round(avg_tokens, 2),
    }
