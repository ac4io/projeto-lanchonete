# lanchonete_backend/app/routers/establishments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud
from app.database import get_db
from app.routers.users import get_current_user # Para autenticação
from app.models import User # Para tipagem do current_user
from app import models # Importa models para poder usar models.Establishment

router = APIRouter(
    prefix="/establishments",
    tags=["Establishments"]
)

@router.post("/", response_model=schemas.EstablishmentResponse, status_code=status.HTTP_201_CREATED)
async def create_establishment(
    establishment: schemas.EstablishmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente proprietários podem criar estabelecimentos."
        )
    # Verifica se o usuário já possui um estabelecimento
    existing_establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
    if existing_establishment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este proprietário já possui um estabelecimento."
        )

    # Passa o owner_id diretamente para a função CRUD
    return await crud.create_establishment(db=db, establishment=establishment, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.EstablishmentResponse])
async def read_establishments(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protege a rota, mas permite visibilidade pública ou filtrada
):
    # Lógica para filtrar estabelecimentos:
    # Se o usuário for um proprietário, mostra apenas o seu próprio estabelecimento.
    # Se for um cliente comum, mostra todos os estabelecimentos.
    if current_user.is_owner:
        establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
        if establishment:
            return [establishment] # Retorna uma lista contendo apenas o estabelecimento do proprietário
        else:
            return [] # Retorna lista vazia se o proprietário não tiver um estabelecimento
    else: # Usuário comum
        establishments = await crud.get_establishments(db, skip=skip, limit=limit)
        return establishments

@router.get("/{establishment_id}", response_model=schemas.EstablishmentResponse)
async def read_establishment(establishment_id: int, db: AsyncSession = Depends(get_db)):
    db_establishment = await crud.get_establishment(db, establishment_id=establishment_id)
    if db_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")
    return db_establishment

@router.put("/{establishment_id}", response_model=schemas.EstablishmentResponse)
async def update_establishment(
    establishment_id: int,
    establishment_update: schemas.EstablishmentCreate, # Reutiliza o schema de criação para atualização
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_establishment = await crud.get_establishment(db, establishment_id=establishment_id)
    if db_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")

    # Autorização: Apenas o proprietário do estabelecimento pode atualizá-lo
    if db_establishment.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a atualizar este estabelecimento")

    updated_establishment = await crud.update_establishment(db, establishment_id=establishment_id, establishment_update=establishment_update)
    return updated_establishment

@router.delete("/{establishment_id}", status_code=status.HTTP_200_OK)
async def delete_establishment(
    establishment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_establishment = await crud.get_establishment(db, establishment_id=establishment_id)
    if db_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")

    # Autorização: Apenas o proprietário do estabelecimento pode deletá-lo
    if db_establishment.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a deletar este estabelecimento")
    
    result = await crud.delete_establishment(db, establishment_id=establishment_id)
    return result