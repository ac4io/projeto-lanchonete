# lanchonete_backend/main.py

from fastapi import FastAPI
from app.database import engine, Base
import asyncio
from app import models # Importa todos os modelos definidos em models.py
from fastapi.middleware.cors import CORSMiddleware

# Importa TODOS os routers que você criou
from app.routers import products
from app.routers import users
from app.routers import establishments
from app.routers import categories
from app.routers import orders 

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="API de Lanchonete",
    description="API para gerenciamento de pedidos e produtos de lanchonete.",
    version="1.0.0",
    # Adicione a configuração de segurança OpenAPI para JWT
    openapi_extra={
        "security": [
            {"BearerAuth": []} # Nome do esquema de segurança que você definirá abaixo
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": { # Nome do esquema de segurança
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Insira o token JWT com o prefixo 'Bearer '"
                }
            }
        }
    }
)

origins = [
    "http://localhost",
    "http://localhost:8000", # Porta do seu FastAPI
    "http://localhost:5173", # Porta padrão do Vite/React, se estiver usando ou quiser testar com ele
    "http://localhost:54270", # <--- **IMPORTANTE**: Adicione a porta em que seu APP FLUTTER WEB está rodando!
                              # Você pode ver essa porta no terminal quando você roda `flutter run -d chrome`
                              # Geralmente é algo como 5XXXX ou 6XXXX.
                              # Ex: "http://localhost:58432"
    "http://10.0.2.2:8000",   # Para emulador Android acessar o FastAPI
    "http://127.0.0.1:8000",
    "http://192.168.X.X:8000", # Se você estiver testando em um dispositivo físico, adicione o IP da sua máquina aqui
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
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

# Inclui os routers na aplicação principal (apenas uma vez para cada)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(establishments.router)
app.include_router(categories.router)
app.include_router(orders.router)

# Define a rota raiz (endpoint) (já configurado)
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API da Lanchonete!"}