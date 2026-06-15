"""Model: Fornecedor + Tabela Associativa N:N com Componente."""

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from backend.database import Base


class Fornecedor(Base):
    __tablename__ = "fornecedor"

    id_fornecedor = Column(Integer, primary_key=True, autoincrement=True)
    cnpj          = Column(String(18), nullable=False, unique=True)
    razao_social  = Column(String(150), nullable=False)
    nome_fantasia = Column(String(150), nullable=True)
    email         = Column(String(100), nullable=True)
    telefone      = Column(String(20), nullable=True)
    cep           = Column(String(10), nullable=True)
    logradouro    = Column(String(150), nullable=True)
    numero        = Column(String(10), nullable=True)
    bairro        = Column(String(80), nullable=True)
    cidade        = Column(String(80), nullable=True)
    estado        = Column(String(2), nullable=True)


class FornecedorComponente(Base):
    """Tabela associativa N:N — Fornecedor ↔ Componente."""

    __tablename__ = "fornecedor_componente"

    id_forn_comp            = Column(Integer, primary_key=True, autoincrement=True)
    id_fornecedor           = Column(
        Integer,
        ForeignKey("fornecedor.id_fornecedor", ondelete="CASCADE"),
        nullable=False,
    )
    id_componente           = Column(
        Integer,
        ForeignKey("componente.id_componente", ondelete="CASCADE"),
        nullable=False,
    )
    preco_unitario          = Column(Numeric(10, 2), nullable=True)
    prazo_entrega_dias      = Column(Integer, nullable=True)
    fornecedor_preferencial = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint(
            "id_fornecedor", "id_componente", name="uq_forn_comp"
        ),
    )
