# lanchonete_backend/app/schemas.py

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field # Importa Field para exemplo de validação, se precisar
from datetime import datetime
# --- SCHEMAS EXISTENTES (apenas para contexto) ---

# Usuários
class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_owner: Optional[bool] = False # Adicionado para diferenciar proprietários

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    # Remove hashed_password da resposta
    class Config:
        from_attributes = True # ou orm_mode = True (dependendo da versão do Pydantic)

# Token (já corrigido na etapa anterior)
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    is_owner: Optional[bool] = None

# --- NOVAS E/OU REESTRUTURADAS CLASSES PARA ESTABELECIMENTOS ---

# Base para criação/atualização: o que o cliente envia na requisição
class EstablishmentBase(BaseModel):
    name: str
    address: str
    phone: str # Pode usar Field(..., pattern="^\d{10,11}$") para validação de formato
    description: Optional[str] = None

# Schema para criar um estabelecimento (não inclui owner_id, pois será definido no backend)
class EstablishmentCreate(EstablishmentBase):
    pass # Herda tudo de EstablishmentBase, não adiciona owner_id aqui

# Schema para a resposta de um estabelecimento (inclui id e owner_id)
class EstablishmentResponse(EstablishmentBase):
    id: int
    owner_id: int # Este campo é retornado na resposta
    # Adicionar outras relações aqui se quiser que elas sejam incluídas na resposta
    # products: List["ProductResponse"] = [] # Exemplo de como incluir produtos
    # orders: List["OrderResponse"] = [] # Exemplo de como incluir pedidos

    class Config:
        from_attributes = True # Permite mapeamento de ORM (SQLAlchemy)

# --- SCHEMAS PARA PRODUTOS (apenas para contexto) ---

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_available: bool = True
    establishment_id: int # O ID do estabelecimento ao qual o produto pertence
    category_id: Optional[int] = None # ID da categoria (pode ser nulo)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel): # Schema para atualização (campos opcionais)
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    establishment_id: Optional[int] = None
    category_id: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    # Opcional: incluir o estabelecimento e a categoria completos
    # establishment: Optional["EstablishmentResponse"] = None # Cuidado com importação circular
    # category: Optional["CategoryResponse"] = None # Cuidado com importação circular
    class Config:
        from_attributes = True

# --- SCHEMAS PARA CATEGORIAS ---

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# --- SCHEMAS PARA PEDIDOS ---

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    price_at_time_of_order: float # Preço do produto no momento do pedido
    # Opcional: incluir o produto completo
    # product: ProductResponse # Cuidado com importação circular
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    establishment_id: int
    status: str = "pending" # Pode usar Enum para estados
    delivery_address: Optional[str] = None
    is_pickup: bool = False
    payment_method: str # Pode usar Enum para métodos de pagamento

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] # Lista de itens no pedido

class OrderUpdate(BaseModel):
    status: Optional[str] = None # Permite atualizar apenas o status
    delivery_address: Optional[str] = None
    is_pickup: Optional[bool] = None
    payment_method: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    customer_id: int # O ID do cliente que fez o pedido
    total_amount: float
    order_date: datetime # Importar datetime de algum lugar
    items: List[OrderItemResponse] = [] # Inclui os itens do pedido na resposta
    # Opcional: incluir o cliente e o estabelecimento completos
    # customer: UserResponse # Cuidado com importação circular
    # establishment: EstablishmentResponse # Cuidado com importação circular
    class Config:
        from_attributes = True

# --- Ajustes para evitar referência circular (se você adicionar as relações de volta) ---
# Se você decidir adicionar as relações complexas (ex: ProductResponse.establishment),
# pode precisar usar `update_forward_refs()` no final do arquivo schemas.py ou
# usar Pydantic V2 e `from __future__ import annotations` e aspas nos tipos.
# No momento, como os exemplos estão comentados, não é necessário.