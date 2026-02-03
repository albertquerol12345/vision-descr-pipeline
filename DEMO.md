# Vision Pipeline — Demo Guide

Enrich image catalogs with AI descriptions.

---

## 🎯 What You'll See

**Before:** CSV with image paths but no descriptions  
**After:** Same CSV with SEO-friendly descriptions (80-100 words each)

Example:
```csv
image_id,image_path,description_es,words_count
ring_001,images/gold_ring.jpg,"Elegant anillo de oro amarillo de 18k con diseño minimalista...",87
```

---

## 🚀 Quick Demo

```bash
# Setup
git clone https://github.com/albertquerol12345/vision-descr-pipeline.git
cd vision_descr_pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add API key
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-...
```

### Option 1: Use Sample Data (Recommended)

```bash
# The repo includes 2 sample images
ls images/
# sample_001.png sample_002.png

# Run on 2 sample images
python -m src.main describe-all
```

**Expected output:**
```
Loading config from config.toml
Found 2 images to process
✓ sample_001.png → 89 words
✓ sample_002.png → 94 words

Checkpoint saved: data/creatives_master.csv
Total cost: ~$0.0002
```

### Option 2: Use Your Own Images

```bash
# 1. Place images in images/ folder
# 2. Create input CSV
echo "image_id,image_path,source
prod_001,images/my_product_1.jpg,catalog
prod_002,images/my_product_2.jpg,catalog" > data/creatives_input.csv

# 3. Run
python -m src.main describe-all
```

---

## 📊 Sample Output

### Input (`data/creatives_input.csv`)
```csv
image_id,image_path,source,product_type
ring_001,images/ring_gold.jpg,catalog,jewelry
ring_002,images/ring_silver.jpg,catalog,jewelry
```

### Output (`data/creatives_master.csv`)
```csv
image_id,image_path,source,product_type,description_es,words_count,runtime_ms
ring_001,images/ring_gold.jpg,catalog,jewelry,"Anillo de oro amarillo de 18 quilates con acabado pulido brillante. Diseño clásico y atemporal perfecto para uso diario o eventos especiales. La banda de 4mm ofrece un equilibrio entre elegancia y comodidad.",87,1240
ring_002,images/ring_silver.jpg,catalog,jewelry,"Anillo de plata esterlina 925 con diseño moderno y líneas geométricas. Acabado mate que resalta la textura del metal. Ideal para quienes buscan piezas contemporáneas y versátiles.",94,1180
```

---

## 🖼️ Visual Walkthrough

| Step | What Happens |
|------|--------------|
| 1 | Script reads CSV and finds images without `description_es` |
| 2 | Each image is base64-encoded and sent to OpenAI Vision |
| 3 | API returns description (constrained to 80-100 words) |
| 4 | Row is appended to output CSV immediately |
| 5 | Every 5 rows, checkpoint is saved to disk |
| 6 | Progress bar shows ETA and cost estimate |

---

## 🔍 Resumability Demo

The killer feature: stop and resume anytime.

```bash
# Start processing 100 images
python -m src.main describe-all
# Press Ctrl+C after 12 images

# Resume later
python -m src.main describe-all
# Picks up from image 13, skips first 12
```

**Why this matters:** API failures, rate limits, or laptop shutdowns don't lose progress.

---

## 💰 Cost Estimation

Real numbers from OpenAI pricing (GPT-4o-mini):

| Volume | Input Tokens | Output Tokens | Total Cost |
|--------|--------------|---------------|------------|
| 10 images | ~8K | ~700 | ~$0.002 |
| 100 images | ~80K | ~7K | ~$0.015 |
| 400 images | ~320K | ~28K | ~$0.04 |
| 1,000 images | ~800K | ~70K | ~$0.10 |

*Based on 80-100 words (~70 tokens) output per image.*

---

## 🎓 Configuration Options

Edit `config.toml`:

```toml
[paths]
input_csv = "data/creatives_input.csv"
output_csv = "data/creatives_master.csv"
images_folder = "images"

[generation]
# Model selection
model = "gpt-4o-mini"  # Cheapest, good quality
# model = "gpt-4o"     # Higher quality, 10x cost

# Word count constraints
target_min_words = 80
target_max_words = 100

# Checkpoint frequency (rows)
save_every = 5

# Retry config
max_retries = 3
retry_delay = 2.0
```

---

## 🧪 Sample Images

The repo includes 2 sample images for testing:

```bash
ls images/
├── sample_001.png
└── sample_002.png
```

Use these to test your setup before processing real data.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API rate limit" | Increase `retry_delay` in config |
| "Image not found" | Check `images_folder` path in config |
| Descriptions too long | Lower `target_max_words` |
| Costs too high | Switch to `gpt-4o-mini` if using `gpt-4o` |

---

## 💡 Pro Use Cases

1. **Batch product uploads** — Generate descriptions for 1000 new SKUs overnight
2. **SEO refresh** — Re-describe old products with better keywords
3. **Translation** — Generate descriptions in Spanish, then translate batch
4. **A/B testing** — Generate 2 variants per product, test which converts better
