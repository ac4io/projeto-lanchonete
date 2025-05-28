from unittest import skip
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app import models, schemas # Importa seus modelos e schemas

# ====================================================================
# Operações CRUD para Produtos
# ====================================================================

#Função para obter um produto pelo ID
async def get_product(db: AsyncSession, product_id: int):
    # 'select(models.Product)' cria uma query para selecionar da tabela de Produtos
    # '.where(models.Product.id == product_id)' filtra pelo ID
    # '.first()' tenta obter o primeiro resultado (ou None se não encontrar)
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    return result.scalars().first()

# Função para obter múltiplos produtos
async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Product).offset(skip).limit(limit))
    return result.scalars().all()

# Função para criar um novo produto
async def create_product(db: AsyncSession, product: schemas.ProductCreate):
    # Cria uma instância do modelo SQLAlchemy a partir dos dados do schema Pydantic
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        is_available=product.is_available,
        establishment_id=product.establishment_id,
        category_id=product.category_id
    )
    db.add(db_product) #Adiciona o objeto ao banco de dados
    await db.commit() #Salva as mudanças no banco
    await db.refresh(db_product) #Atualiza o objeto com os dados do banco
    return db_product

# Função para atualizar um produto existente
async def update_product(db: AsyncSession, product_id: int, product_update: schemas.ProductUpdate):
    db_product = await get_product(db,product_id)
    if db_product:
        # Atualiza apenas os campos que foram fornecidos na requisição
        update_data = product_update.model_dump(exclude_unset=True)# Exclui campos não definidos
        for key, value in update_data.items():
            setattr(db_product, key, value) # Define o atributo no objeto do banco
        await db.commit()
        await db.refresh(db_product)
    return db_product

# Função para deletar um produto
async def delete_product(db: AsyncSession, product_id: int):
    db_product = await get_product(db, product_id)
    if db_product:
        await db.delete(db_product) # Marca o objeto para exclusão
        await db.commit() #Confirma a exclusão
        return {"message": "Produto deletado com sucesso!"}
    return None

# ====================================================================
# Operações CRUD para Categorias (Exemplo)
# ====================================================================
# Apenas um exemplo rápido para que você possa adicionar categorias
async def create_category(db: AsyncSession, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def get_category(db: AsyncSession, category_id: int):
    result = await db.execute(select(models.Category).where(models.Category.id == category_id))
    return result.scalars().first()

async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Category).offset(skip).limit(limit))
    return result.scalars().all()

# Você pode adicionar funções update_category e delete_category de forma similar aos produtos.
