# lanchonete_backend/app/models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base # Importa a Base do seu arquivo database.py

# ====================================================================
# Modelos de Usuário (Cliente e Proprietário)
# ====================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_owner = Column(Boolean, default=False) # Para diferenciar cliente de proprietário

    orders = relationship("Order", back_populates="customer")

# ====================================================================
# Modelo de Estabelecimento (Lanchonete)
# ====================================================================

class Establishment(Base):
    __tablename__ = "establishments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    owner = relationship("User", backref="establishment", primaryjoin="Establishment.owner_id == User.id")
    products = relationship("Product", back_populates="establishment")
    orders = relationship("Order", back_populates="establishment")

# ====================================================================
# Modelo de Categoria de Produto
# ====================================================================

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    products = relationship("Product", back_populates="category")

# ====================================================================
# Modelo de Produto
# ====================================================================

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True) # URL da imagem do produto (e.g., S3/GCS)
    is_available = Column(Boolean, default=True) # Se o produto está disponível ou esgotado

    establishment_id = Column(Integer, ForeignKey("establishments.id"), nullable=False)
    establishment = relationship("Establishment", back_populates="products")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True) # Pode não ter categoria
    category = relationship("Category", back_populates="products")

    # Relacionamento com ItemPedido (muitos-para-muitos através de OrderItem)
    order_items = relationship("OrderItem", back_populates="product")

# ====================================================================
# Modelo de Pedido
# ====================================================================

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    establishment_id = Column(Integer, ForeignKey("establishments.id"), nullable=False)
    order_date = Column(DateTime, default=func.now())
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending") # Ex: pending, preparing, on_delivery, delivered, cancelled, ready_for_pickup
    delivery_address = Column(String, nullable=True) # Preenchido se for delivery
    is_pickup = Column(Boolean, default=False) # True se for retirada no local
    payment_method = Column(String, nullable=False) # Ex: credit_card, cash, pix

    # Relacionamentos
    customer = relationship("User", back_populates="orders")
    establishment = relationship("Establishment", back_populates="orders")
    items = relationship("OrderItem", back_populates="order") # Itens deste pedido

# ====================================================================
# Modelo de Item do Pedido (Tabela de Junção para Pedido-Produto)
# ====================================================================

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time_of_order = Column(Float, nullable=False) # Preço do produto no momento do pedido

    # Relacionamentos
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")