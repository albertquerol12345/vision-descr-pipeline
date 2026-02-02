# Vision Description Pipeline (Portfolio Copy)

![Vision Description preview](assets/preview.gif)

Lightweight Python pipeline to generate consistent image descriptions via a vision API and consolidate them into a master CSV.

## Quick start
```bash
cd VISION_DESCR_PIPELINE
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# add OPENAI_API_KEY

python -m src.main describe-all
```

## Sample data
This portfolio copy includes a tiny sample CSV in `data/creatives_input.csv` with placeholder images.
Replace with your own images and metadata.

## Expected output (sample)
- Enriched CSV example: `data/creatives_output_sample.csv`
- Preview:
  ![Vision Description output](assets/preview.gif)

## Repo structure
- `src/` CLI and API calls
- `config.toml` pipeline settings
- `data/` input/output CSVs
- `images/` image root folder

## Notes
- Full technical README is in `README_FULL.md`.
