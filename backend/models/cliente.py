"""Model: Cliente (Pessoa Jurídica)."""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql import func
from backend.database import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente    = Column(Integer, primary_key=True, autoincrement=True)
    cnpj          = Column(String(18), nullable=False, unique=True, index=True)
    razao_social  = Column(String(150), nullable=False)
    nome_fantasia = Column(String(150), nullable=True)
    email         = Column(String(100), nullable=False, unique=True)
    telefone      = Column(String(20), nullable=True)
    cep           = Column(String(10), nullable=True)
    logradouro    = Column(String(150), nullable=True)
    numero        = Column(String(10), nullable=True)
    complemento   = Column(String(50), nullable=True)
    bairro        = Column(String(80), nullable=True)
    cidade        = Column(String(80), nullable=True)
    estado        = Column(String(2), nullable=True)
    data_cadastro = Column(Date, nullable=False, default=func.current_date())
