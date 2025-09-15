from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == user_in.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
        user = User(email=user_in.email, hashed_password=hash_password(user_in.password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}
