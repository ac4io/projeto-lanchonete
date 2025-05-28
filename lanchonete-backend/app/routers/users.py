# lanchonete_backend/app/routers/users.py

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Para formulário de login
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud
from app.database import get_db
from app.security import (
    create_access_token, # <-- CORRIGIDO: 'access' com dois 's'
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    decode_access_token # <-- CORRIGIDO: 'access' com dois 's'
)
from app.models import User # Para o CurrentUser dependency

# Para a autenticação usando OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token") # Define a URL para obter o token

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# --- Dependência para obter o usuário logado ---
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme) # <-- CORRIGIDO AQUI: Usando oauth2_scheme
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token) # <-- CORRIGIDO: 'access' com dois 's'
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = await crud.get_user_by_email(db, user.email) # <-- Já estava certo, mantido
    if user is None:
        raise credentials_exception
    return user

# --- Endpoints de Autenticação ---

@router.post("/register/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado")
    return await crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token( # <-- CORRIGIDO: 'access' com dois 's'
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_email(db, form_data.username) # <-- Corrigido aqui também, se não estava
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # <-- CORRIGIDO: 'access' com dois 's'
    access_token = create_access_token( # <-- CORRIGIDO: 'access' com dois 's'
        data={"sub": user.email, "is_owner": user.is_owner}, # Adiciona is_owner ao token
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} # <-- CORRIGIDO: 'access' com dois 's'

# --- Endpoints de Usuário (Protegidos) ---

@router.get("/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário logado."""
    return current_user

@router.get("/", response_model=List[schemas.UserResponse])
async def read_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Exemplo de rota protegida
):
    """Lista todos os usuários (apenas para usuários autenticados)."""
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users