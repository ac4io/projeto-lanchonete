# lanchonete_backend/main.py

from fastapi import FastAPI
from app.database import engine, Base
import asyncio
from app import models # Importa todos os modelos definidos em models.py

# Importa os routers que você criou
from app.routers import products
# Você adicionará outros routers aqui: from app.routers import users, orders, categories, establishments

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="API de Lanchonete",
    description="API para gerenciamento de pedidos e produtos de lanchonete.",
    version="1.0.0"
)

# Função para criar as tabelas no banco de dados (já configurado)
async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Evento de startup para criar as tabelas (já configurado)
@app.on_event("startup")
async def startup_event():
    print("Criando tabelas do banco de dados (se não existirem)...")
    await create_db_tables()
    print("Tabelas criadas ou já existentes.")

# Inclui os routers na aplicação principal
app.include_router(products.router)
# Você adicionará outros routers aqui:
# app.include_router(users.router)
# app.include_router(orders.router)
# app.include_router(categories.router)
# app.include_router(establishments.router)


# Define a rota raiz (endpoint) (já configurado)
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API da Lanchonete!"}