# auth.py
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Base class for DB models
Base = declarative_base()

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Define User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

# ✅ SQLite database
engine = create_engine("sqlite:///./users.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Create the table
Base.metadata.create_all(bind=engine)


# ✅ Utilities to access/modify users
def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email).first()


def create_user(db, email, password):
    hashed = pwd_context.hash(password)
    user = User(email=email, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(password, hash):
    return pwd_context.verify(password, hash)
