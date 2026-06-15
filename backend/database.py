"""
Configuração do banco de dados SQLite com SQLAlchemy.
Camada de Dados — Arquitetura 3 Camadas.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/madeira_verde.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


# Habilita FK do SQLite a cada conexão
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency Injection — fornece sessão para cada requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria todas as tabelas no banco."""
    # Importa todos os models para registrar no metadata
    from backend.models import (  # noqa: F401
        cliente,
        componente,
        empregado,
        empresa_manutencao,
        encomenda,
        fornecedor,
        manutencao,
        produto,
    )
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado com sucesso.")
