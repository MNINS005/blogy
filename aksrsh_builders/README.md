# Blogy — AI Blog Engine 🚀
**Prompt & Profit · Bizmark'26 Hackathon Prototype**

A fully functional AI-powered blog generation engine that converts keyword intent into high-ranking, GEO-optimized, conversion-focused blogs through a structured prompt flow.

---

## 📁 Project Structure

```
blogy/
├── backend/
│   ├── main.py           ← FastAPI backend (all logic)
│   └── requirements.txt
└── frontend/
    └── index.html        ← Single-file UI (open in browser)
```

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-...

# Windows
set ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start the backend
```bash
uvicorn main:app --reload --port 8000
```

### 4. Open the frontend
Simply open `frontend/index.html` in any browser. No build step needed.

---

## 🏗️ Architecture: 7-Step Prompt Pipeline

```
Keyword Input
     │
     ▼
[Step 1] Keyword Research
  Seed keyword → LSI cluster expansion (7 variants per keyword)
     │
     ▼
[Step 2] Intent Mapping
  Informational + Commercial intent blend
  (Top-of-funnel awareness + bottom-of-funnel conversion)
     │
     ▼
[Step 3] SERP Gap Identification
  4 structural content gaps identified programmatically
  (snippet opportunities, FAQ schema, depth gaps, GEO gaps)
     │
     ▼
[Step 4] Prompt Injection
  Keyword placement rules hard-encoded into the system prompt:
  - Title (H1), First 100 words, 2+ H2 headings, Conclusion
     │
     ▼
[Step 5] GEO Signal Injection
  Location-specific context for India/US/UK/SEA/Global
     │
     ▼
[Step 6] AI Generation (Claude claude-opus-4-5)
  Structured markdown blog with meta description
     │
     ▼
[Step 7] SEO Validation (Post-generation)
  All metrics computed programmatically on the generated text
```

---

## 📊 SEO Metrics Computed

| Metric | Method |
|---|---|
| Keyword Density | n-gram sliding window count / total words × 100 |
| Readability Score | Flesch Reading Ease (sentence length + syllable ratio) |
| Snippet Readiness | Heuristic: headings + lists + definitions + length + question words |
| AI Naturalness Score | Sentence length variance + contractions + question marks |
| Keyword Placement Score | Title / first 100 words / H2 headings / last 100 words |
| Heading Structure Score | H1 count + H2 count ≥ 3 + H3 count ≥ 2 |
| CTA Effectiveness | Count of conversion phrases (get started, try now, etc.) |
| SEO Optimization % | Weighted average of all above metrics |
| Projected Traffic | Bucketed: High/Medium/Low based on SEO% |
| SERP Gap Analysis | 4 static strategic gaps per generation |
| Internal Linking | 4 contextual link suggestions per blog |
| Keyword Clusters | 4 intent clusters (Informational/Transactional/Navigational/Commercial) |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/generate` | Generate full blog + SEO metrics |
| POST | `/analyze-seo` | Analyze any content against a keyword |
| GET | `/health` | Model + status info |

### POST /generate — Request Body
```json
{
  "keyword": "AI blog automation tool India",
  "target_audience": "startups and businesses in India",
  "tone": "professional",
  "word_count": 1200,
  "include_cta": true,
  "geo_location": "India"
}
```

### POST /generate — Response
```json
{
  "title": "...",
  "content": "...(markdown)...",
  "meta_description": "...",
  "focus_keyword": "...",
  "lsi_keywords": [...],
  "seo_metrics": {
    "keyword_density": 1.2,
    "readability_score": 68.4,
    "snippet_readiness": 80.0,
    "seo_optimization_percentage": 76.3,
    ...
  },
  "prompt_architecture": {
    "step_1_keyword_research": "...",
    ...
  }
}
```

---

## 🖥️ Frontend Features

- **Blog Preview tab** — Full rendered blog with meta description, word count, SEO score badge, copy & download buttons
- **SEO Dashboard tab** — 8 metric cards with progress bars, SERP gap analysis, internal linking suggestions, traffic potential
- **Prompt Architecture tab** — Live 7-step breakdown of the pipeline used
- **Keyword Clusters tab** — LSI keywords as chips + 4 intent clusters

---

## 📝 Part 3 — Blog Titles to Publish

Generate and publish these two blogs from the UI:
1. **"Blogy – Best AI Blog Automation Tool in India"**
2. **"How Blogy is Disrupting Martech – Organic Traffic on Autopilot, Cheapest SEO"**

Recommended publishing platforms (from the approved list):
- Medium, LinkedIn Articles, Dev.to, Hashnode, Substack

---

## 📦 Tech Stack

- **Backend**: Python, FastAPI, Anthropic SDK (Claude claude-opus-4-5)
- **Frontend**: Vanilla HTML/CSS/JS (zero dependencies, single file)
- **SEO Engine**: Custom Python algorithms (no external API required)
- **Model**: Claude claude-opus-4-5 via Anthropic Messages API
