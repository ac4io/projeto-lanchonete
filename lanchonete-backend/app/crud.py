# lanchonete_backend/app/crud.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime # Importa datetime para pedidos

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

async def create_establishment(db: AsyncSession, establishment: schemas.EstablishmentCreate, owner_id: int): # <--- ATENÇÃO AQUI: owner_id deve estar presente
    db_establishment = models.Establishment(
        name=establishment.name,
        address=establishment.address,
        phone=establishment.phone,
        description=establishment.description,
        owner_id=owner_id
    )
    db.add(db_establishment)
    await db.commit()
    await db.refresh(db_establishment)
    return db_establishment

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

async def create_order(db: AsyncSession, order: schemas.OrderCreate, customer_id: int): # <--- ADICIONE customer_id aqui
    total_amount = 0
    order_items_models = []

    for item_data in order.items:
        product = await get_product(db, item_data.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {item_data.product_id} not found.")

        # Calculate price_at_time_of_order
        price_at_time_of_order = product.price
        total_amount += price_at_time_of_order * item_data.quantity

        order_item = models.OrderItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price_at_time_of_order=price_at_time_of_order
        )
        order_items_models.append(order_item)

    db_order = models.Order(
        establishment_id=order.establishment_id,
        customer_id=customer_id, # <--- Use o customer_id passado como argumento
        status=order.status,
        delivery_address=order.delivery_address,
        is_pickup=order.is_pickup,
        payment_method=order.payment_method,
        total_amount=total_amount,
        order_date=datetime.now()
    )

    db.add(db_order)
    await db.flush() # flush para que db_order.id seja populado antes de adicionar os itens

    for order_item_model in order_items_models:
        order_item_model.order_id = db_order.id # Associa o item ao pedido
        db.add(order_item_model)

    await db.commit()
    await db.refresh(db_order)

    # Carregar as relações para a resposta
    # Isso é importante para que o OrderResponse inclua os itens
    await db.refresh(db_order, attribute_names=["items"])
    for item in db_order.items:
        await db.refresh(item, attribute_names=["product"]) # Se OrderItem.product estiver no schemas.OrderItemResponse

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
        # Deleta os itens do pedido primeiro
        await db.execute(delete(models.OrderItem).where(models.OrderItem.order_id == order_id))
        await db.delete(db_order)
        await db.commit()
        return {"message": "Pedido deletado com sucesso!"}
    return None

# Importações necessárias para as novas funções de pedido (coloque no topo do arquivo crud.py)
from sqlalchemy.orm import selectinload
from sqlalchemy import delete