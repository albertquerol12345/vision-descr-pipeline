# Vision Description Pipeline — Technical Demonstration

![Architecture](https://img.shields.io/badge/Architecture-CLI%20Pipeline%20%2B%20API%20Integration-blue)
![Resumable](https://img.shields.io/badge/Feature-Resumable-orange)
![Cost](https://img.shields.io/badge/Demo%20Cost-%240.03%2F400%20images-green)

**A technical demonstration of resilient batch processing with external APIs.**

This is not a commercial image management tool. It is a **sandbox** demonstrating:
- Resumable batch processing (checkpointing)
- API cost optimization
- CSV data pipelines
- Error handling in long-running processes

> **For recruiters/reviewers:** See [What to Evaluate](#what-to-evaluate) section below.

---

## 🎯 The Core Demonstration

**Problem:** Enrich 400 product images with AI-generated descriptions without losing progress on API failures.  
**Approach:** CLI pipeline with checkpointing every N rows.  
**Demonstration:** Process a batch, stop halfway, resume seamlessly.

```
Input CSV → Check for existing descriptions → 
→ Call OpenAI Vision API → Update CSV → 
→ Save checkpoint every 5 rows → Repeat
```

---

## ⚡ Quick Start

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add: OPENAI_API_KEY=sk-...

# Run demonstration
python -m src.main describe-all
```

**What happens:**
1. Reads `data/creatives_input.csv`
2. Skips rows that already have descriptions (idempotent)
3. Calls OpenAI Vision API for each new image
4. Updates `data/creatives_master.csv` incrementally
5. Saves checkpoint every 5 rows

---

## 📸 What It Actually Looks Like

### Terminal Output

```
$ python -m src.main describe-all

Loading config from config.toml
Found 45 images to process
✓ IMG_001.jpg → 87 words (saved)
✓ IMG_002.jpg → 94 words (saved)
✓ IMG_003.jpg → 82 words (saved)
✓ IMG_004.jpg → 91 words (saved)
✓ IMG_005.jpg → 88 words (checkpoint saved)
✓ IMG_006.jpg → 79 words (saved)
...

Checkpoint saved: 40/45 processed
Cost estimate: ~$0.003

$ python -m src.main describe-all
Resuming from checkpoint...
✓ IMG_041.jpg → 85 words (saved)
✓ IMG_042.jpg → 92 words (saved)
...
Complete! 45/45 processed
```

### Output CSV Structure

```csv
image_id,image_path,description_es,words_count,runtime_ms
ring_001,images/ring.jpg,"Anillo de oro amarillo de 18k...",87,1240
ring_002,images/necklace.jpg,"Collar de plata con diseño moderno...",94,1180
```

---

## 🔍 What to Evaluate

**If you're a technical reviewer, focus on:**

| Aspect | Where to Look | What Demonstrates |
|--------|---------------|-------------------|
| **Resilience** | `src/describe_images.py` | Checkpointing every N rows |
| **Idempotency** | Main loop logic | Skips already-processed items |
| **API Efficiency** | Prompt engineering | 80-100 words = cost control |
| **Error Handling** | Retry logic | Exponential backoff for API failures |
| **Data Integrity** | CSV updates | Atomic writes, no data loss |

**Key Implementation Details:**

1. **Checkpointing Strategy**
   ```python
   if processed_count % config.save_every == 0:
       df.to_csv(output_path, index=False)
       print(f"Checkpoint saved: {processed_count}/{total}")
   ```

2. **Idempotency Check**
   ```python
   if pd.notna(row.get('description_es')) and row['description_es'].strip():
       continue  # Skip already processed
   ```

3. **Cost Control**
   - Target: 80-100 words (vs 200+ default)
   - Model: GPT-4o-mini (cheapest viable option)
   - Result: ~$0.03 for 400 images

---

## 📊 Demo Scale Reality Check

| Metric | Value | Context |
|--------|-------|---------|
| Processing rate | 60-120/hour | API rate limits, not code speed |
| Checkpoint frequency | Every 5 rows | Configurable via `config.toml` |
| Cost per image | ~$0.0001 | GPT-4o-mini pricing |
| Cost for 400 images | ~$0.03 | Documented and verifiable |

**This is not a production DAM (Digital Asset Management) system.** Scaling would require:
- Queue system for API calls
- Parallel processing
- Database instead of CSV
- Image CDN integration

---

## 🛠️ Stack & Patterns

**Core:**
- Python 3.10+
- Pandas for CSV manipulation
- OpenAI Python client
- TOML for configuration

**Patterns Demonstrated:**
- Pipeline pattern (input → process → output)
- Checkpoint/restore (resumable processing)
- Configuration-driven behavior
- CLI interface with argparse

---

## 💡 Why This Exists

I built this pipeline to demonstrate:
1. **Resilient batch processing** — Long-running jobs that survive interruptions
2. **API cost consciousness** — Optimizing prompts for cost, not just quality
3. **Data pipeline architecture** — CSV as poor-man's database, with integrity checks
4. **Error handling** — Graceful degradation when external APIs fail

It's not a product. It's a **technical demonstration** of patterns needed for any serious data processing work.

---

## 📚 Documentation

- [DEMO.md](DEMO.md) — Step-by-step with sample data
- [config.toml](config.toml) — All configuration options
- `data/creatives_output_sample.csv` — Example output format

---

## 🎓 Use Cases (If This Were a Product)

- **E-commerce:** Auto-generate product descriptions at scale
- **Fashion/Jewelry:** Consistent tone across thousands of SKUs
- **SEO:** Batch-describe image alt-text
- **DAM enrichment:** Add metadata to digital asset libraries

---

*Questions about the pipeline architecture? Open an issue or email: albert.querol.beltran@gmail.com*
