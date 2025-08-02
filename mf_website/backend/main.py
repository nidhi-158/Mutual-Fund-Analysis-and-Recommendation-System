from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
import pandas as pd


from database import SessionLocal, get_db, engine
from models import User
import models


from nav_live_fetcher import fetch_latest_nav
from nav_live_merge import merge_live_with_features
from recommend_logic import recommend_for_existing_investor, recommend_for_new_investor


# ------------------
# App & Config Setup
# ------------------
models.Base.metadata.create_all(bind=engine)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------
# Models
# ------------------
class UserCreate(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ExistingInvestorRequest(BaseModel):
    scheme_id: int
    nav_at_purchase: float
    units_held: float
    purchase_date: str


class NewInvestorRequest(BaseModel):
    budget: float
    risk_level: str
    asset_class: str
    market_cap: str


# ------------------
# Auth Utility Functions
# ------------------
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str):
    hashed_pw = pwd_context.hash(password)
    new_user = User(email=email, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------
# Auth Endpoints
# ------------------
@app.post("/register", response_model=TokenResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="⚠ User already registered. Please log in.")
    create_user(db, user.email, user.password)
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login", response_model=TokenResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="⚠ No user found. Please register first.")
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="❌ Incorrect password.")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# ------------------
# Recommendation Endpoints
# ------------------
@app.post("/recommend/existing")
def existing_investor(data: ExistingInvestorRequest):
    try:
        feature_df = pd.read_csv("phase5_processed_funds_data_final.csv", parse_dates=["Date"])
        feature_df["Scheme"] = feature_df["Scheme"].astype(str).str.strip().str.lower()


        live_nav_df = fetch_latest_nav()
        df = merge_live_with_features(feature_df, live_nav_df)


        return recommend_for_existing_investor(
            df,
            data.scheme_id,
            data.nav_at_purchase,
            data.units_held,
            data.purchase_date
        )
    except Exception as e:
        print("❌ Error in /recommend/existing:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/recommend/new")
def new_investor(data: NewInvestorRequest):
    try:
        feature_df = pd.read_csv("phase5_processed_funds_data_final.csv", parse_dates=["Date"])
        feature_df["Scheme"] = feature_df["Scheme"].astype(str).str.strip().str.lower()


        live_nav_df = fetch_latest_nav()
        df = merge_live_with_features(feature_df, live_nav_df)


        print("\n🟨 New Investor Input Debug:")
        print(f"  ▶ Budget: {data.budget}")
        print(f"  ▶ Risk Level: {data.risk_level}")
        print(f"  ▶ Asset Class: {data.asset_class}")
        print(f"  ▶ Market Cap: {data.market_cap}")
        print(f"  ▶ df shape after merge: {df.shape}")
        print(f"  ▶ Sample df:\n{df[['Scheme', 'NAV', 'Date']].sort_values('Date', ascending=False).head(3)}")


        result = recommend_for_new_investor(
            df,
            data.budget,
            data.risk_level,
            data.asset_class,
            data.market_cap
        )


        print("✅ Final Recommendation:", result)
        return result


    except Exception as e:
        print("❌ Error in /recommend/new:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/schemes")
def get_scheme_list():
    schemes_1 = pd.read_csv("phase5_processed_funds_data_final.csv", usecols=["SchemeID"])
    schemes_2 = pd.read_csv("AFTER_PHASE_2_with_balance_FINAL.csv", usecols=["SchemeID", "Scheme"])
    schemes_2["Scheme"] = schemes_2["Scheme"].astype(str).str.strip().str.lower()
    merged = pd.merge(schemes_1.drop_duplicates(), schemes_2.drop_duplicates(), on="SchemeID", how="left")
    return merged.dropna().drop_duplicates().to_dict(orient="records")
