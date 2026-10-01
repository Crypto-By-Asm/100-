from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.database import get_db
from models.blog import BlogPost
from services.blog_service import DEFAULT_TOPICS, generate_and_save_batch, get_or_create_posts
from config.settings import settings
from auth.deps import get_current_user
from models.user import User

router = APIRouter()

@router.get("/topics")
async def blog_topics():
    return {
        "auto_generation_enabled": settings.blog_auto_generate,
        "planned_batch_size": settings.blog_batch_size,
        "topics": DEFAULT_TOPICS[:30],
    }

@router.get("/posts")
def list_posts(
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    posts = (
        db.query(BlogPost)
        .filter(BlogPost.is_published == True)
        .order_by(BlogPost.published_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "meta_description": p.meta_description,
            "excerpt": p.excerpt,
            "category": p.category,
            "reading_time_minutes": p.reading_time_minutes,
            "published_at": p.published_at.isoformat() if p.published_at else None,
            "is_ai_generated": p.is_ai_generated,
        }
        for p in posts
    ]

@router.get("/posts/{slug}")
def get_post(slug: str, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.slug == slug, BlogPost.is_published == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "meta_description": post.meta_description,
        "content": post.content,
        "excerpt": post.excerpt,
        "keywords": post.keywords,
        "category": post.category,
        "reading_time_minutes": post.reading_time_minutes,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "is_ai_generated": post.is_ai_generated,
    }

@router.post("/generate")
def generate_blogs(
    count: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a small batch of AI blog articles.
    Requires authentication. Limited to control API cost.
    """
    if not settings.blog_auto_generate:
        raise HTTPException(status_code=400, detail="Blog auto-generation is disabled")
    results = generate_and_save_batch(db, count=count)
    return {"generated": results, "count": len([r for r in results if r.get("success")])}
