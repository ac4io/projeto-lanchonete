from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud
from app.database import get_db
from app.routers.users import get_current_user # Para autenticação
from app.models import User # Para tipagem do current_user

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protegido: requer autenticação
):
    # Opcional: Você pode adicionar lógica aqui para verificar se apenas proprietários podem criar categorias
    # Por exemplo: if not current_user.is_owner: raise HTTPException(...)
    return await crud.create_category(db=db, category=category)

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def read_category(category_id: int, db: AsyncSession = Depends(get_db)):
    db_category = await crud.get_category(db, category_id=category_id)
    if db_category is  None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return db_category

@router.put("/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: int,
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #Autorização: Apenas propietários ou admins podem atualizar categorias
    if not current_user.is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a atualizar categoriasa")
    
    db_category = await crud.update_category(db, category_id=category_id, category_update=category)
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #Autorização: Apenas propietários podem deletar categorias
    if not current_user.is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a deletar categorias")
    
    result = await crud.delete_category(db, category_id=category_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return result