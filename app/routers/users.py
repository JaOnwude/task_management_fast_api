from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import require_api_key, PaginationParams
from app.models import User, UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[str, Depends(require_api_key)],  # Protected
):
    # Check if username or email already exists
    existing_user = session.exec(
        select(User).where((User.username == user.username) | (User.email == user.email))
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already registered.",
        )

    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserPublic])
def read_users(
    session: Annotated[Session, Depends(get_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    statement = select(User).offset(pagination.offset).limit(pagination.limit)
    return session.exec(statement).all()


@router.get("/{user_id}", response_model=UserPublic)
def read_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user