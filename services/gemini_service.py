import json
from config.settings import settings

def _get_client():
    if not settings.gemini_api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        return client
    except Exception:
        return None

def explain_signal(signal: dict) -> str:
    """
    Generate a clear, educational explanation of the signal using Gemini.
    Never invents market data. Stays within the provided indicators and plan.
    """
    client = _get_client()
    if client is None:
        return (
            "Gemini AI is not configured. Add your GEMINI_API_KEY to the .env file "
            "to enable AI-powered signal explanations."
        )

    prompt = f"""
You are a professional crypto market analyst for "Crypto Bot by ASM Traders".
Explain the following trading signal in clear, educational English (or simple Urdu mixed if natural).

IMPORTANT RULES:
- Do NOT invent any numbers or market data.
- Do NOT claim guaranteed profits or high win rates.
- Base the explanation ONLY on the provided data.
- Mention risks and invalidation conditions.
- Keep it under 220 words.
- Be professional and neutral.

SIGNAL DATA:
{json.dumps(signal, indent=2)}

Structure your response as:
1. What the signal is saying
2. Key supporting evidence from indicators
3. Risk management levels
4. What would invalidate this idea
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"AI explanation temporarily unavailable. ({type(e).__name__})"

def generate_blog_article(topic: str, language: str = "en") -> dict:
    """
    Generate a full SEO-friendly educational blog article on the given topic.
    """
    client = _get_client()
    if client is None:
        return {
            "success": False,
            "error": "Gemini API key not configured",
            "title": topic,
            "content": "",
        }

    prompt = f"""
You are an expert SEO content writer for a crypto education website called "Crypto Bot by ASM Traders".

Write a complete, high-quality educational blog article on this topic:
"{topic}"

Requirements:
- Language: {language}
- Length: 900–1400 words
- Professional, clear, beginner-to-intermediate friendly
- Include practical examples related to crypto markets
- Use markdown headings (##, ###)
- Never promise guaranteed profits
- End with a short educational summary

Also return the following metadata in a clean JSON-like structure at the very end after the article:

---META---
{{
  "title": "SEO optimized title under 60 characters",
  "slug": "url-friendly-slug",
  "meta_description": "compelling meta description under 155 characters",
  "keywords": "keyword1, keyword2, keyword3, keyword4, keyword5",
  "excerpt": "2-3 sentence summary",
  "reading_time_minutes": 6,
  "category": "Technical Analysis"
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.text.strip()

        # Parse meta
        if "---META---" in text:
            content_part, meta_part = text.split("---META---", 1)
            content = content_part.strip()
            try:
                # Clean possible markdown code fences
                meta_clean = meta_part.strip()
                if meta_clean.startswith("```"):
                    meta_clean = meta_clean.split("```")[1]
                    if meta_clean.startswith("json"):
                        meta_clean = meta_clean[4:]
                meta = json.loads(meta_clean.strip())
            except Exception:
                meta = {
                    "title": topic,
                    "slug": topic.lower().replace(" ", "-")[:80],
                    "meta_description": topic[:150],
                    "keywords": "crypto, trading, analysis",
                    "excerpt": topic,
                    "reading_time_minutes": 5,
                    "category": "Education",
                }
        else:
            content = text
            meta = {
                "title": topic,
                "slug": topic.lower().replace(" ", "-")[:80],
                "meta_description": topic[:150],
                "keywords": "crypto, trading, analysis",
                "excerpt": topic,
                "reading_time_minutes": 5,
                "category": "Education",
            }

        return {
            "success": True,
            "title": meta.get("title", topic),
            "slug": meta.get("slug", topic.lower().replace(" ", "-")[:80]),
            "meta_description": meta.get("meta_description", ""),
            "keywords": meta.get("keywords", ""),
            "excerpt": meta.get("excerpt", ""),
            "reading_time_minutes": meta.get("reading_time_minutes", 5),
            "category": meta.get("category", "Education"),
            "content": content,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "title": topic,
            "content": "",
        }
