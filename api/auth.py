from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from config.database import get_db
from config.settings import settings
from models.user import User, SubscriptionPlan
from auth.security import get_password_hash, verify_password, create_access_token
from auth.deps import get_current_user
from services.demo_service import ensure_demo_account

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)
    full_name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    plan: str
    is_active: bool

def seed_plans(db: Session):
    if db.query(SubscriptionPlan).count() == 0:
        plans = [
            SubscriptionPlan(
                name="free",
                price_monthly=0.0,
                signals_per_day=10,
                demo_balance=10000.0,
                has_ai_explanations=False,
                has_blog_access=True,
                description="Free plan with limited daily signals and demo trading.",
            ),
            SubscriptionPlan(
                name="pro",
                price_monthly=29.0,
                signals_per_day=100,
                demo_balance=50000.0,
                has_ai_explanations=True,
                has_blog_access=True,
                description="Pro plan with AI explanations and higher limits.",
            ),
            SubscriptionPlan(
                name="elite",
                price_monthly=79.0,
                signals_per_day=999,
                demo_balance=100000.0,
                has_ai_explanations=True,
                has_blog_access=True,
                description="Elite plan for serious traders.",
            ),
        ]
        db.add_all(plans)
        db.commit()

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    seed_plans(db)
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username.lower()).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    free_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "free").first()
    user = User(
        email=payload.email.lower(),
        username=payload.username.lower(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name or payload.username,
        plan_id=free_plan.id if free_plan else 1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create demo account
    ensure_demo_account(db, user)

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "plan": user.plan.name if user.plan else "free",
        },
    }

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "plan": user.plan.name if user.plan else "free",
        },
    }

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "plan": current_user.plan.name if current_user.plan else "free",
        "is_active": current_user.is_active,
        "plan_details": {
            "signals_per_day": current_user.plan.signals_per_day if current_user.plan else 10,
            "has_ai_explanations": current_user.plan.has_ai_explanations if current_user.plan else False,
            "demo_balance": current_user.plan.demo_balance if current_user.plan else 10000,
        },
    }

@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    seed_plans(db)
    plans = db.query(SubscriptionPlan).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price_monthly": p.price_monthly,
            "signals_per_day": p.signals_per_day,
            "demo_balance": p.demo_balance,
            "has_ai_explanations": p.has_ai_explanations,
            "description": p.description,
        }
        for p in plans
    ]
