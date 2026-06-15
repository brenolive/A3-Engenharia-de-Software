"""Model: Produto + Tabelas Associativas."""

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from backend.database import Base


class Produto(Base):
    __tablename__ = "produto"

    id_produto     = Column(Integer, primary_key=True, autoincrement=True)
    codigo         = Column(String(30), nullable=False, unique=True)
    nome           = Column(String(150), nullable=False)
    descricao      = Column(Text, nullable=True)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    categoria      = Column(String(80), nullable=True)
    ativo          = Column(Boolean, nullable=False, default=True)


class ProdutoComponente(Base):
    """Tabela associativa N:N — Produto ↔ Componente."""

    __tablename__ = "produto_componente"

    id_prod_comp          = Column(Integer, primary_key=True, autoincrement=True)
    id_produto            = Column(
        Integer,
        ForeignKey("produto.id_produto", ondelete="CASCADE"),
        nullable=False,
    )
    id_componente         = Column(
        Integer,
        ForeignKey("componente.id_componente", ondelete="RESTRICT"),
        nullable=False,
    )
    quantidade_necessaria = Column(Numeric(10, 3), nullable=False)
    unidade_medida        = Column(String(20), nullable=False, default="un")
    tempo_uso_horas       = Column(Numeric(8, 2), nullable=True)
    observacao            = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("id_produto", "id_componente", name="uq_prod_comp"),
    )


class ProdutoMaoObra(Base):
    """Tabela associativa N:N — Produto ↔ Empregado (Mão de Obra)."""

    __tablename__ = "produto_maoobra"

    id_prod_mo        = Column(Integer, primary_key=True, autoincrement=True)
    id_produto        = Column(
        Integer,
        ForeignKey("produto.id_produto", ondelete="CASCADE"),
        nullable=False,
    )
    id_empregado      = Column(
        Integer,
        ForeignKey("empregado.id_empregado", ondelete="RESTRICT"),
        nullable=False,
    )
    horas_necessarias = Column(Numeric(8, 2), nullable=False)
    funcao_no_produto = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint("id_produto", "id_empregado", name="uq_prod_emp"),
    )
