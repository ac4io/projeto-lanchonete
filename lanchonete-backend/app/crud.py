# lanchonete_backend/app/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime # Importa datetime para pedidos
from sqlalchemy.orm import selectinload # Para carregar relações em pedidos
from sqlalchemy import delete # Para usar na exclusão de itens de pedido

from app import models, schemas
from app.security import get_password_hash

# ====================================================================
# Operações CRUD para Usuários
# ====================================================================

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_owner=user.is_owner
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# ====================================================================
# Operações CRUD para Estabelecimentos
# ====================================================================

async def get_establishment(db: AsyncSession, establishment_id: int):
    result = await db.execute(select(models.Establishment).where(models.Establishment.id == establishment_id))
    return result.scalars().first()

async def get_establishment_by_owner_id(db: AsyncSession, owner_id: int):
    result = await db.execute(select(models.Establishment).where(models.Establishment.owner_id == owner_id))
    return result.scalars().first()

async def get_establishments(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Establishment).offset(skip).limit(limit))
    return result.scalars().all()

async def create_establishment(db: AsyncSession, establishment: schemas.EstablishmentCreate, owner_id: int):
    db_establishment = models.Establishment(
        name=establishment.name,
        address=establishment.address,
        phone=establishment.phone,
        description=establishment.description,
        owner_id=owner_id # Agora owner_id vem como argumento separado
    )
    db.add(db_establishment)
    await db.commit()
    await db.refresh(db_establishment)
    return db_establishment

async def update_establishment(db: AsyncSession, establishment_id: int, establishment_update: schemas.EstablishmentCreate):
    db_establishment = await get_establishment(db, establishment_id)
    if db_establishment:
        update_data = establishment_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_establishment, key, value)
        await db.commit()
        await db.refresh(db_establishment)
    return db_establishment

async def delete_establishment(db: AsyncSession, establishment_id: int):
    db_establishment = await get_establishment(db, establishment_id)
    if db_establishment:
        # Opcional: considerar deletar produtos relacionados ou definir owner_id como NULL
        await db.delete(db_establishment)
        await db.commit()
        return {"message": "Estabelecimento deletado com sucesso!"}
    return None

# ====================================================================
# Operações CRUD para Categorias
# ====================================================================

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

async def update_category(db: AsyncSession, category_id: int, category_update: schemas.CategoryCreate):
    db_category = await get_category(db, category_id)
    if db_category:
        db_category.name = category_update.name
        await db.commit()
        await db.refresh(db_category)
    return db_category

async def delete_category(db: AsyncSession, category_id: int):
    db_category = await get_category(db, category_id)
    if db_category:
        await db.delete(db_category)
        await db.commit()
        return {"message": "Categoria deletada com sucesso!"}
    return None

# ====================================================================
# Operações CRUD para Produtos
# ====================================================================

async def get_product(db: AsyncSession, product_id: int):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    return result.scalars().first()

async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Product).offset(skip).limit(limit))
    return result.scalars().all()

async def create_product(db: AsyncSession, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        is_available=product.is_available,
        establishment_id=product.establishment_id,
        category_id=product.category_id
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product(db: AsyncSession, product_id: int, product_update: schemas.ProductUpdate):
    db_product = await get_product(db, product_id)
    if db_product:
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        await db.commit()
        await db.refresh(db_product)
    return db_product

async def delete_product(db: AsyncSession, product_id: int):
    db_product = await get_product(db, product_id)
    if db_product:
        await db.delete(db_product)
        await db.commit()
        return {"message": "Produto deletado com sucesso!"}
    return None

# ====================================================================
# Operações CRUD para Pedidos
# ====================================================================

async def create_order(db: AsyncSession, order: schemas.OrderCreate):
    db_order = models.Order(
        customer_id=order.customer_id,
        establishment_id=order.establishment_id,
        total_amount=0.0, # Será calculado a partir dos itens
        status=order.status,
        delivery_address=order.delivery_address,
        is_pickup=order.is_pickup,
        payment_method=order.payment_method,
        order_date=datetime.utcnow() # Data do pedido
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    total_amount = 0.0
    for item_data in order.items:
        # Obtém o produto para pegar o preço atual
        product = await get_product(db, item_data.product_id)
        if not product:
            # Isso deve ser tratado no router antes de chamar o CRUD,
            # mas mantemos aqui para robustez ou testes diretos
            raise ValueError(f"Produto com ID {item_data.product_id} não encontrado.")

        # Define o preço do item no momento do pedido
        item_price = product.price

        db_order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price_at_time_of_order=item_price
        )
        db.add(db_order_item)
        total_amount += (item_price * item_data.quantity)

    db_order.total_amount = total_amount # Atualiza o total do pedido
    await db.commit()
    await db.refresh(db_order) # Refreshes novamente para incluir os itens se necessário na resposta
    return db_order

async def get_order(db: AsyncSession, order_id: int):
    result = await db.execute(
        select(models.Order)
        .where(models.Order.id == order_id)
        .options(
            # Carrega relações para exibição completa do pedido
            selectinload(models.Order.customer),
            selectinload(models.Order.establishment),
            selectinload(models.Order.items).selectinload(models.OrderItem.product)
        )
    )
    return result.scalars().first()

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Order)
        .offset(skip).limit(limit)
        .options(
            # Carrega relações para exibição completa dos pedidos
            selectinload(models.Order.customer),
            selectinload(models.Order.establishment),
            selectinload(models.Order.items).selectinload(models.OrderItem.product)
        )
    )
    return result.scalars().all()

async def update_order(db: AsyncSession, order_id: int, order_update: schemas.OrderUpdate):
    db_order = await get_order(db, order_id)
    if db_order:
        update_data = order_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        await db.commit()
        await db.refresh(db_order)
    return db_order

async def delete_order(db: AsyncSession, order_id: int):
    db_order = await get_order(db, order_id)
    if db_order:
        # Deleta os itens do pedido primeiro para evitar erro de chave estrangeira
        await db.execute(delete(models.OrderItem).where(models.OrderItem.order_id == order_id))
        await db.delete(db_order)
        await db.commit()
        return {"message": "Pedido deletado com sucesso!"}
    return None