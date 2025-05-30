from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.orm import selectinload

from app import schemas, crud
from app.database import get_db
from app.routers.users import get_current_user # Para autenticação
from app.models import User # Para tipagem do current_user

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order:schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verifica se os produtos existem e são do estabelecimento correto
    for item in order.items:
        product = await crud.get_product(db, item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item.product_id} não encontrado." 
            )
        if product.establishment_id != order.establishment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto com ID {item.product_id} não pertence ao estabelecimento {order.establishment_id}"
            )
    db_order = await crud.create_order(db=db, order=order, customer_id=current_user.id)
    return db_order

@router.get("/", response_model=List[schemas.OrderResponse])
async def read_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Requer autenticação
):
    #Lógica para filtrar pedidos:
    # - Se for propietário, mostrar apenas pedidos do seu estabelecimento.
    # - Se for cliente, mostrar apenas seus próprios pedidos.
    # - Se for um admin(futuro), mostrar todos os pedidos.

    # Por enquanto, vamos simplificar para que clientes vejam seus pedidos
    # e proprietários vejam os pedidos do seu estabelecimento

    orders = []
    if current_user.is_owner:
        establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
        if establishment:
            result = await db.execute(
                select(models.Order)
                .where(models.Order.establishment_id == establishment.id)
                .offset(skip)
                .limit(limit)
                .options(
                    selectinload(models.Order.customer),
                    selectinload(models.Order.establishment),
                    selectinload(models.Order.items).selectinload(models.OrderItem.product)
                )
            )
            orders = result.scalars().all()
    else: # Usuário comum
        result = await db.execute(
            select(models.Order)
            .where(models.Order.customer_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(models.Order.customer),
                selectinload(models.Order.establishment),
                selectinload(models.Order.items).selectinload(models.OrderItem.product)
            )
        )
        orders = result.scalars().all()

    return orders

@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def read_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = await crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    
    # Autorização: Cliente só vê seus próprios pedidos, propietário vê pedidos do seu estabelecimento
    if current_user.is_owner:
        establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
        if not establishment or db_order.establishment_id != establishment.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a ver este pedido")
    elif db_order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a ver este pedido")
    
    return db_order

@router.put("/{order_id}", response_model=schemas.OrderResponse)
async def update_order(
    order_id: int,
    order_update: schemas.OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = await crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    
    # Autorização: Apenas o proprietário do estabelecimento pode atualizar o pedido
    establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
    if not current_user.is_owner or not establishment or db_order.establishment_id != establishment.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Não autorizado a atualizar este pedido")
    
    updated_order = await crud.update_order(db, order_id=order_id, order_update=order_update)
    return update_order

@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
async def delete_order(
    order_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_order = await crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    
    # Autorização: Apenas o proprietário do estabelecimento ou o cliente que fez o pedido pode deletar
    # (Ou apenas o proprietário/admin, dependendo da regra de negócio)
    # Aqui, vamos permitir que o proprietário do estabelecimento ou o cliente deletem o pedido.

    is_owner_of_establishment = False
    if current_user.is_owner:
        establishment = await crud.get_establishment_by_owner_id(db, current_user.id)
        if establishment and db_order.establishment_id == establishment.id:
            is_owner_of_establishment = True

    if not is_owner_of_establishment and db_order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a deletar este pedido")
    
    result = await crud.delete_order(db, order_id=order_id)
    return result