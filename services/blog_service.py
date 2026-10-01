from sqlalchemy.orm import Session
from models.blog import BlogPost
from services.gemini_service import generate_blog_article
from config.settings import settings
import re

DEFAULT_TOPICS = [
    "How crypto market volatility works",
    "How RSI is used in crypto analysis",
    "MACD explained for crypto traders",
    "EMA and trend identification",
    "What is ADX in technical analysis",
    "How volume confirms market moves",
    "Support and resistance basics",
    "How stop loss works",
    "How take profit works",
    "Risk reward ratio explained",
    "What is paper trading",
    "How backtesting works",
    "Multi timeframe crypto analysis",
    "Common crypto trading mistakes",
    "How to build a trading plan",
    "What is market liquidity",
    "Crypto candlestick basics",
    "How volatility affects stop loss",
    "How to avoid overtrading",
    "Understanding crypto market cycles",
    "Bitcoin dominance explained",
    "Altcoin market analysis basics",
    "Crypto trading indicators overview",
    "Why signals can fail",
    "How to evaluate a trading strategy",
    "Demo trading vs live trading",
    "How to read a crypto chart",
    "Trading psychology basics",
    "Risk management for beginners",
    "Crypto trading glossary",
]

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:120]

def get_or_create_posts(db: Session, limit: int = 30) -> list[BlogPost]:
    existing = db.query(BlogPost).order_by(BlogPost.id).limit(limit).all()
    if existing:
        return existing
    return []

def generate_and_save_batch(db: Session, count: int = 5) -> list[dict]:
    """
    Generate a batch of blog articles using Gemini and save them.
    Limited batch size to control API cost.
    """
    existing_slugs = {p.slug for p in db.query(BlogPost.slug).all()}
    results = []

    for topic in DEFAULT_TOPICS:
        if len(results) >= count:
            break
        slug = slugify(topic)
        if slug in existing_slugs:
            continue

        article = generate_blog_article(topic, language=settings.blog_language)
        if not article.get("success"):
            results.append({"topic": topic, "success": False, "error": article.get("error")})
            continue

        post = BlogPost(
            title=article["title"],
            slug=article.get("slug") or slug,
            meta_description=article.get("meta_description", "")[:320],
            content=article["content"],
            excerpt=article.get("excerpt", "")[:500],
            keywords=article.get("keywords", "")[:500],
            category=article.get("category", "Education"),
            reading_time_minutes=article.get("reading_time_minutes", 5),
            is_ai_generated=True,
            is_published=True,
        )
        db.add(post)
        existing_slugs.add(post.slug)
        results.append({"topic": topic, "success": True, "slug": post.slug, "title": post.title})

    db.commit()
    return results
