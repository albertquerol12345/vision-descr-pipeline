from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .describe_images import AppConfig, describe_images, load_config, resume_stats, setup_logging


def run_describe(args: argparse.Namespace) -> None:
    cfg = load_config(Path(args.config) if args.config else None)
    setup_logging(cfg.log_file)
    logging.info("Iniciando describe-all")
    processed, skipped, total_words, total_tokens = describe_images(cfg)
    logging.info(
        "Proceso completado: %s descritas, %s saltadas, %s palabras (≈%s tokens)",
        processed,
        skipped,
        total_words,
        total_tokens,
    )


def run_resume(args: argparse.Namespace) -> None:
    cfg = load_config(Path(args.config) if args.config else None)
    stats = resume_stats(cfg)
    print("Resumen de creatives_master.csv")
    print(f"Filas totales: {stats['total_rows']}")
    print(f"Con descripción: {stats['with_description']}")
    print(f"Palabras totales: {stats['words_total']}")
    print(f"Tokens estimados: {stats['tokens_total']}")
    print(f"Media palabras/imagen: {stats['avg_words']}")
    print(f"Media tokens/imagen: {stats['avg_tokens']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline de descripciones de imágenes")
    parser.add_argument("--config", help="Ruta opcional al config.toml", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    describe_cmd = subparsers.add_parser("describe-all", help="Generar descripciones para todas las imágenes")
    describe_cmd.set_defaults(func=run_describe)

    resume_cmd = subparsers.add_parser("resume-stats", help="Mostrar resumen del CSV maestro")
    resume_cmd.set_defaults(func=run_resume)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
