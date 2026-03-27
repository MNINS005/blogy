from urllib import response
from xml.parsers.expat import model

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import re
import math
#import google.generativeai as genai
from dotenv import load_dotenv
import os

from openai import OpenAI

load_dotenv()

#api_key = os.getenv("API_KEY")
#genai.configure(api_key=api_key)
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
app = FastAPI(title="Blogy AI Blog Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



# ─── Request / Response Models ────────────────────────────────────────────────

class BlogRequest(BaseModel):
    keyword: str
    target_audience: str = "startups and businesses"
    tone: str = "professional"
    word_count: int = 1200
    include_cta: bool = True
    geo_location: str = "India"

class SEOMetrics(BaseModel):
    keyword_density: float
    keyword_count: int
    word_count: int
    readability_score: float
    readability_grade: str
    snippet_readiness: float
    ai_naturalness_score: float
    keyword_placement_score: float
    heading_structure_score: float
    cta_effectiveness: float
    internal_linking_suggestions: list[str]
    keyword_clusters: list[str]
    serp_gap_analysis: list[str]
    seo_optimization_percentage: float
    projected_traffic_potential: str

class BlogResponse(BaseModel):
    title: str
    content: str
    meta_description: str
    focus_keyword: str
    lsi_keywords: list[str]
    seo_metrics: SEOMetrics
    prompt_architecture: dict


# ─── SEO Analysis Helpers ─────────────────────────────────────────────────────

def compute_keyword_density(text: str, keyword: str) -> tuple[float, int]:
    words = re.findall(r'\b\w+\b', text.lower())
    kw_words = keyword.lower().split()
    count = 0
    for i in range(len(words) - len(kw_words) + 1):
        if words[i:i+len(kw_words)] == kw_words:
            count += 1
    density = (count / len(words) * 100) if words else 0
    return round(density, 2), count

def compute_readability(text: str) -> tuple[float, str]:
    """Flesch Reading Ease approximation"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', text)
    syllables = sum(count_syllables(w) for w in words)
    
    if not sentences or not words:
        return 50.0, "Standard"
    
    avg_sentence_len = len(words) / len(sentences)
    avg_syllables_per_word = syllables / len(words)
    score = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word)
    score = max(0, min(100, score))
    
    if score >= 70: grade = "Easy (Great for web)"
    elif score >= 50: grade = "Standard"
    elif score >= 30: grade = "Difficult"
    else: grade = "Very Difficult"
    
    return round(score, 1), grade

def count_syllables(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    return max(1, count)

def compute_snippet_readiness(content: str) -> float:
    score = 0.0
    if re.search(r'\n#{1,3}\s', content): score += 20
    if re.search(r'\*\*.*?\*\*', content): score += 15
    if re.search(r'^\s*[-*]\s', content, re.MULTILINE): score += 15
    if re.search(r'^\s*\d+\.\s', content, re.MULTILINE): score += 15
    if len(content) > 800: score += 20
    if re.search(r'(what is|how to|why|when|definition)', content, re.IGNORECASE): score += 15
    return min(100.0, score)

def compute_keyword_placement(content: str, keyword: str) -> float:
    kw = keyword.lower()
    score = 0.0
    lines = content.split('\n')
    # In title (first heading)
    for line in lines[:5]:
        if kw in line.lower() and line.startswith('#'):
            score += 30
            break
    # In first 100 words
    first_100 = ' '.join(re.findall(r'\b\w+\b', content)[:100])
    if kw in first_100.lower(): score += 25
    # In headings
    headings = [l for l in lines if re.match(r'^#{1,3}\s', l)]
    if any(kw in h.lower() for h in headings): score += 25
    # In last 100 words
    last_100 = ' '.join(re.findall(r'\b\w+\b', content)[-100:])
    if kw in last_100.lower(): score += 20
    return min(100.0, score)

def compute_heading_structure(content: str) -> float:
    h1 = len(re.findall(r'^# ', content, re.MULTILINE))
    h2 = len(re.findall(r'^## ', content, re.MULTILINE))
    h3 = len(re.findall(r'^### ', content, re.MULTILINE))
    score = 0.0
    if h1 == 1: score += 30
    if h2 >= 3: score += 40
    if h3 >= 2: score += 30
    return min(100.0, score)

def compute_cta_effectiveness(content: str) -> float:
    cta_phrases = ['get started', 'try now', 'sign up', 'learn more', 'contact us',
                   'book a demo', 'start free', 'free trial', 'get access', 'visit', 'click']
    count = sum(1 for p in cta_phrases if p in content.lower())
    return min(100.0, count * 20)

def compute_ai_naturalness(content: str) -> float:
    """Heuristic: checks for varied sentence length, contractions, conversational phrases"""
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences: return 50.0
    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    variety_score = min(40, math.sqrt(variance) * 3)
    contractions = len(re.findall(r"\b(it's|don't|can't|we're|you're|isn't|won't|they're)\b", content))
    contraction_score = min(30, contractions * 5)
    questions = len(re.findall(r'\?', content))
    question_score = min(30, questions * 10)
    return round(variety_score + contraction_score + question_score + 10, 1)

def generate_seo_metrics(content: str, keyword: str) -> SEOMetrics:
    kd, kc = compute_keyword_density(content, keyword)
    readability, grade = compute_readability(content)
    words = re.findall(r'\b\w+\b', content)
    snippet = compute_snippet_readiness(content)
    naturalness = compute_ai_naturalness(content)
    kp_score = compute_keyword_placement(content, keyword)
    heading_score = compute_heading_structure(content)
    cta_score = compute_cta_effectiveness(content)
    
    # Overall SEO %
    seo_pct = round((kp_score * 0.25 + heading_score * 0.2 + snippet * 0.2 +
                     min(100, readability) * 0.15 + min(100, (1.5 - abs(kd - 1.5)) * 66) * 0.2), 1)
    
    traffic = "High (5K–20K/mo)" if seo_pct > 75 else "Medium (1K–5K/mo)" if seo_pct > 55 else "Low (<1K/mo)"
    
    lsi = [f"{keyword} tool", f"best {keyword}", f"{keyword} software", f"free {keyword}",
           f"{keyword} for business", f"AI {keyword}", f"{keyword} India"]
    
    clusters = [
        f"Informational: 'what is {keyword}', 'how does {keyword} work'",
        f"Transactional: 'buy {keyword}', '{keyword} pricing', '{keyword} free trial'",
        f"Navigational: '{keyword} login', '{keyword} dashboard'",
        f"Commercial: 'best {keyword}', '{keyword} review', '{keyword} vs competitors'"
    ]
    
    serp_gaps = [
        "No featured snippet targeting current top results — opportunity to capture position 0",
        "Competitor pages lack structured FAQ sections — add FAQ schema markup",
        "Low content depth on 'pricing comparison' subtopic — expand this section",
        "Missing GEO-specific content for Tier-2 Indian cities — opportunity to rank locally"
    ]
    
    internal_links = [
        f"Link to '/blog/what-is-{keyword.replace(' ', '-')}' from intro section",
        f"Add link to '/pricing' page near CTA section",
        f"Cross-link to '/features' page from the benefits section",
        f"Link to '/case-studies' from the results/proof section"
    ]
    
    return SEOMetrics(
        keyword_density=kd,
        keyword_count=kc,
        word_count=len(words),
        readability_score=readability,
        readability_grade=grade,
        snippet_readiness=round(snippet, 1),
        ai_naturalness_score=round(naturalness, 1),
        keyword_placement_score=round(kp_score, 1),
        heading_structure_score=round(heading_score, 1),
        cta_effectiveness=round(cta_score, 1),
        internal_linking_suggestions=internal_links,
        keyword_clusters=clusters,
        serp_gap_analysis=serp_gaps,
        seo_optimization_percentage=seo_pct,
        projected_traffic_potential=traffic
    )


# ─── Blog Generation ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert SEO content strategist and blog writer. 
You write high-ranking, GEO-optimized, conversion-focused blog posts.
Always structure blogs with:
- A compelling H1 title (use the focus keyword naturally)
- An engaging intro paragraph (include keyword in first 100 words)
- At least 4-5 H2 subheadings 
- H3s under key sections
- Bold text for important points
- Bullet/numbered lists where helpful
- A clear CTA section at the end
- Use markdown formatting throughout
Write naturally — avoid robotic, repetitive AI patterns. Vary sentence lengths.
Include GEO context when specified. Target the given audience."""

def build_blog_prompt(req: BlogRequest) -> str:
    return f"""Generate a complete, SEO-optimized blog post with these specifications:

Focus Keyword: "{req.keyword}"
Target Audience: {req.target_audience}
Tone: {req.tone}
Target Word Count: {req.word_count} words
GEO Target: {req.geo_location}
Include CTA: {req.include_cta}

Requirements:
1. Use the focus keyword in: title, first paragraph, at least 2 H2 headings, conclusion
2. Keyword density should be around 1-1.5%
3. Include LSI keywords naturally (variations and related terms)
4. Structure for featured snippet eligibility (clear definitions, numbered steps, or concise tables)
5. Add a compelling meta description at the END of the blog in this exact format:
   META_DESCRIPTION: [your 155-char meta description here]
6. Use GEO-specific context relevant to {req.geo_location}
7. Make it conversion-focused — include statistics, benefits, and a strong CTA
8. The blog should genuinely help the reader AND position the topic authoritatively

Write the complete blog now:"""

def extract_meta_description(content: str) -> tuple[str, str]:
    match = re.search(r'META_DESCRIPTION:\s*(.+)', content)
    if match:
        meta = match.group(1).strip()
        clean_content = content[:match.start()].strip()
        return clean_content, meta
    return content, f"Discover everything about {content[:100]}..."


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.post("/generate", response_model=BlogResponse)
def generate_blog(req: BlogRequest):
    try:
        prompt = build_blog_prompt(req)
        
        # model = genai.GenerativeModel("gemini-1.5-flash")
        # model = genai.GenerativeModel("gemini-1.5-flash")
        response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    max_tokens=2000,
    temperature=0.7
)
        raw_content = response.choices[0].message.content
        
        content, meta_desc = extract_meta_description(raw_content)
        
        # Extract title from first H1
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        title = title_match.group(1) if title_match else req.keyword
        
        # LSI keywords
        lsi = [
            f"{req.keyword} tool", f"best {req.keyword}",
            f"{req.keyword} software", f"free {req.keyword}",
            f"{req.keyword} for startups", f"AI-powered {req.keyword}",
            f"{req.keyword} {req.geo_location}"
        ]
        
        seo_metrics = generate_seo_metrics(content, req.keyword)
        
        prompt_architecture = {
            "step_1_keyword_research": f"Seed keyword: '{req.keyword}' → expanded to {len(lsi)} LSI variants",
            "step_2_intent_mapping": "Informational + Commercial intent blend for top-of-funnel + conversion",
            "step_3_serp_analysis": "4 SERP gaps identified for featured snippet + local ranking opportunities",
            "step_4_content_brief": f"Target: {req.word_count} words, {req.tone} tone, {req.geo_location} GEO",
            "step_5_prompt_injection": "Keyword placement rules injected: title, intro, H2s, conclusion",
            "step_6_seo_validation": "Post-generation density check, readability scoring, snippet readiness",
            "step_7_geo_optimization": f"GEO signals injected for {req.geo_location} local relevance"
        }
        
        return BlogResponse(
            title=title,
            content=content,
            meta_description=meta_desc,
            focus_keyword=req.keyword,
            lsi_keywords=lsi,
            seo_metrics=seo_metrics,
            prompt_architecture=prompt_architecture
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-seo")
def analyze_seo(keyword: str, content: str):
    try:
        metrics = generate_seo_metrics(content, keyword)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy", "model": "google/gemini-1.5-flash"}
