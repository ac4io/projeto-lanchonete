# lanchonete_backend/app/security.py

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# Configurações de segurança
SECRET_KEY = "sua-chave-secreta-bem-forte-e-randomica" # ATENÇÃO: Mude para uma chave segura em produção!
ALGORITHM = "HS256" # Algoritmo de hash para o JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Tempo de expiração do token de acesso em minutos

# Contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções de Hashing de Senha ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha em texto puro corresponde à senha hashed."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

# --- Funções de JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str: # <-- CORRIGIDO
    """Cria um token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str): # <-- CORRIGIDO
    """Decodifica e valida um token de acesso JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Token inválido ou expirado
        return None