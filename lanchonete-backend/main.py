# lanchonete_backend/main.py

from fastapi import FastAPI
from app.database import engine, Base
import asyncio
from app import models # Importa todos os modelos definidos em models.py

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="API de Lanchonete",
    description="API para gerenciamento de pedidos e produtos de lanchonete.",
    version="1.0.0"
)

# Função para criar as tabelas no banco de dados
async def create_db_tables():
    # Isso fará com que o SQLAlchemy crie todas as tabelas definidas em Base.metadata
    # (que agora inclui os modelos de app.models)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Evento de startup para criar as tabelas
@app.on_event("startup")
async def startup_event():
    print("Criando tabelas do banco de dados (se não existirem)...")
    await create_db_tables()
    print("Tabelas criadas ou já existentes.")

# Define a rota raiz (endpoint)
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API da Lanchonete!"}

# Exemplo de outro endpoint
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}