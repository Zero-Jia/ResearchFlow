from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserInfo

router = APIRouter()

# Swagger 会基于这个生成右上角的 Authorize 按钮
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="token 里没有 sub 字段")

        user_id = int(user_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"token 解析失败: {str(e)}")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail=f"用户不存在，user_id={user_id}")

    return user


@router.post("/auth/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))

    return AuthResponse(
        access_token=token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
        ),
    )


@router.post("/auth/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    token = create_access_token(str(user.id))

    return AuthResponse(
        access_token=token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
        ),
    )


@router.get("/auth/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user)):
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
    )