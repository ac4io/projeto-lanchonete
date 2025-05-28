# lanchonete_backend/app/routers/products.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud # Importa seus schemas e as funções CRUD
from app.database import get_db # Importa a função para obter a sessão do DB
from app.routers.users import get_current_user # <-- ADICIONADO: Para autenticação
from app.models import User # <-- ADICIONADO: Para tipagem do current_user

# Cria um APIRouter. O 'prefix' define o caminho base para todas as rotas neste router.
# 'tags' ajuda a organizar a documentação da API.
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# ====================================================================
# Endpoints para Produtos
# ====================================================================

# Endpoint para criar um novo produto
@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # <-- ADICIONADO: Protege a rota
):
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas proprietários podem criar produtos."
        )

    # Verificação de autorização: o estabelecimento do produto deve pertencer ao usuário logado
    establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
    if not establishment or establishment.id != product.establishment_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode adicionar produtos ao seu próprio estabelecimento."
        )

    db_product = await crud.create_product(db, product=product)
    return db_product

# Endpoint para listar todos os produtos
@router.get("/", response_model=List[schemas.ProductResponse])
async def read_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # Esta rota pode ser pública ou protegida se você quiser filtrar por usuário/estabelecimento.
    # Por enquanto, vou deixá-la acessível a todos sem exigir autenticação.
    # Se quiser proteger: adicione 'current_user: User = Depends(get_current_user)' e a lógica de filtro.
    products = await crud.get_products(db, skip=skip, limit=limit)
    return products

# Endpoint para obter um produto pelo ID
@router.get("/{product_id}", response_model=schemas.ProductResponse)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return db_product

# Endpoint para atualizar um produto
@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate, # <-- Renomeado para clareza
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # <-- ADICIONADO: Protege a rota
):
    db_product = await crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

    # Verificação de autorização: Apenas o proprietário do estabelecimento pode atualizar seus produtos
    establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
    if not establishment or establishment.id != db_product.establishment_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para atualizar este produto."
        )
    # Se o produto_update inclui establishment_id, ele também deve ser verificado para garantir que
    # o proprietário não está movendo o produto para um estabelecimento que não é dele.
    if product_update.establishment_id is not None and product_update.establishment_id != establishment.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode mover produtos para estabelecimentos que não são seus."
        )


    updated_product = await crud.update_product(db, product_id=product_id, product_update=product_update)
    if updated_product is None: # Embora update_product geralmente retorne o objeto ou None se não encontrar
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao atualizar o produto.")
    return updated_product

# Endpoint para deletar um produto
@router.delete("/{product_id}", status_code=status.HTTP_200_OK) # Mudei para 200 OK para retornar mensagem, ou 204 No Content
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # <-- ADICIONADO: Protege a rota
):
    db_product = await crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

    # Verificação de autorização: Apenas o proprietário do estabelecimento pode deletar seus produtos
    establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
    if not establishment or establishment.id != db_product.establishment_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar este produto."
        )

    success = await crud.delete_product(db, product_id=product_id)
    if not success: # O CRUD agora deve retornar True/False ou algo que indique sucesso
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao deletar o produto.")
    return {"message": "Produto deletado com sucesso!"} # Retorna uma mensagem explícita