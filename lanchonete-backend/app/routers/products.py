from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud # Importa seus schemas e as funções CRUD
from app.database import get_db # Importa a função para obter a sessão do DB

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
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    # Você precisaria adicionar lógica aqui para verificar se o usuário é um proprietário
    # e se o estabelecimento_id pertence a ele, mas isso virá na autenticação.
    db_product = await crud.create_product(db, product=product)
    return db_product

# Endpoint para listar todos os produtos
@router.get("/", response_model=List[schemas.ProductResponse])
async def read_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
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
async def update_product(product_id: int, product: schemas.ProductUpdate, db: AsyncSession = Depends(get_db)):
      # Lógica de autorização virá aqui (somente proprietário do estabelecimento pode atualizar)
      db_product = await crud.update_product(db, product_id=product_id, product_update=product)
      if db_product is None:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
      return db_product

# Endpoint para deletar um produto
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    # Lógica de autorização virá aqui (somente proprietário do estabelecimento pode deletar)
    sucess = await crud.delete_product(db,product_id=product_id)
    if sucess is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return # Retorna 204 no Content para deleção bem sucedida