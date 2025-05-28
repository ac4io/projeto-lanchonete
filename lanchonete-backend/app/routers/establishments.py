from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud
from app.database import get_db
from app.models import User,Establishment #Importa Establishment model
from app.routers.users import get_current_user # Para pegar o usuário logado

router = APIRouter(
    prefix="/establishments",
    tags=["Establishments"]
)

# Endpoint para criar um novo estabelecimento
@router.post("/", response_model=schemas.EstablishmentResponse, status_code=status.HTTP_201_CREATED)
async def create_establishment(
    establishment: schemas.EstablishmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Requer autenticação
):
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente proprietários podem criar estabelecimentos."
        )
    #Verifica se o usuário logado já possui um estabelecimento
    existing_establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
    if existing_establishment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este proprietário já possui um estabelecimento registrado."
        )
    #Associa o estabelecimento ao usuário logado (proprietário)
    establishment.owner_id = current_user.id
    db_establishment = await crud.create_establishment(db, establishment=establishment)
    return db_establishment

# Endpoint para listar todos os estabelecimentos
@router.get("/", response_model=List[schemas.EstablishmentResponse])
async def read_establishment(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    # Esta rota não precisa de autenticação para ser pública
    establishments = await db.execute(select(Establishment).offset(skip).limit(limit))
    return establishments.scalars().all()

# Endpoint para obter um estabelecimento por ID
@router.get("/{establishment_id}", response_model=schemas.EstablishmentResponse)
async def read_establishment(establishment_id: int, db: AsyncSession = Depends(get_db)):
    db_establishment = await crud.get_establishment(db, establishment_id=establishment_id)
    if db_establishment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estabelecimento não encontrado")
    return db_establishment

#


