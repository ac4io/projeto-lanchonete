import typing
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ====================================================================
# Schemas de Usuário
# ====================================================================

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    is_owner: Optional[bool] = False

class UserResponse(UserBase):
    id: int
    is_owner: Optional[bool] = False

    class Config:
        from_attributes = True # Permite que Pydantic leia diretamente dos modelos SQLAlchemy

# ====================================================================
# Schemas de Estabelecimento
# ====================================================================

class EstablishmentBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    address: str = Field(..., min_length=5, max_length=200)
    phone: str = Field(..., min_length=8, max_length=20)
    description: Optional[str] = Field(None, max_length=500)

class EstablishmentCreate(EstablishmentBase):
    owner_id: int #ID do usuário propietário

class EstablishmentResponse(EstablishmentBase):
    id: int
    owner_id: int
    #Opcional: para exibir dados do propietário
    owner: Optional[UserResponse] = None

    class Config:
        from_attributes = True

# ====================================================================
# Schemas de Categoria
# ====================================================================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2 ,max_length=50)

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# ====================================================================
# Schemas de Produto
# ====================================================================

class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    is_available: Optional[bool] = True
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    establishment_id: int

class ProductUpdate(ProductBase):
    # Campos que podem ser atualizados. Opcionais, pois nem todos precisam ser alterados
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    category_id: Optional[int] = None
    establishment_id: Optional[int] = None # Para permitir mover produtos ou reatribuir (raro, mas possível)

class ProductResponse(ProductBase):
    id: int
    establishment_id: int
    #Opcional: para exibir dados da categoria e estabelecimento junto
    category: Optional[CategoryResponse] = None
    establishment: Optional[EstablishmentResponse] = None  # Pode não vir com o owner dentro

    class Config:
        from_attributes = True

# ====================================================================
# Schemas de Pedido
# ====================================================================

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    price_at_time_of_order: Optional[float] = None # Pode ser calculado no backend

class OrderItemCreate(OrderItemBase):
    pass #No create, 'price_at_time_of_order' será definido pelo backend

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    #Opcional: para exibir dados do produto junto
    product: Optional[ProductResponse] = None

    class Config: 
        from_attributes = True

class OrderBase(BaseModel):
    total_amount: float = Field(..., gt=0)
    status: Optional[str] = "pending"
    delivery_address: Optional[str] = None
    is_pickup: Optional[bool] = False
    payment_method: str = Field(..., min_length=2, max_length=50)

class OrderCreate(OrderBase):
    customer_id: int
    establishment_id: int
    items: List[OrderItemCreate] #Lista de itens do pedido

class OrderUpdate(BaseModel):
    #campos que o dono pode atualizar no pedido
    status: Optional[str] = None
    delivery_address: Optional[str] = None
    is_pickup: Optional[bool] = True
    payment_method: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    customer_id: int
    establishment_id: int
    order_date: datetime
    #Opcional: para exibir dados do cliente, estabelecimento e itens
    customer: Optional[UserResponse] = None
    establishment: Optional[EstablishmentResponse] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    acess_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None