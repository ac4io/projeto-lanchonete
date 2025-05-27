# lanchonete_backend/app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexão com o banco de dados.
# Para SQLite, 'sqlite+aiosqlite:///./sql_app.db' cria um arquivo 'sql_app.db' na raiz do projeto.
# Para PostgreSQL, seria algo como:
# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@host/dbname"
# Certifique-se de ter o driver 'asyncpg' instalado para PostgreSQL assíncrono.
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

# Cria o "engine" do SQLAlchemy, que é a interface para o banco de dados.
# connect_args={"check_same_thread": False} é necessário apenas para SQLite
# para permitir que múltiplas threads acessem o banco de dados (o que FastAPI faz).
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria uma "sessionmaker" para produzir objetos de sessão.
# expire_on_commit=False evita que os objetos carregados sejam expirados após o commit,
# permitindo acessá-los mesmo depois de fechar a sessão.
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Base para os modelos de banco de dados (nossas tabelas).
Base = declarative_base()

# Função assíncrona para obter uma sessão de banco de dados.
# Usaremos essa função como uma dependência no FastAPI.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session