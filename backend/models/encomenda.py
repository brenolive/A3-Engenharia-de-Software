"""Model: Encomenda + Item de Encomenda."""

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from backend.database import Base


class Encomenda(Base):
    __tablename__ = "encomenda"

    id_encomenda          = Column(Integer, primary_key=True, autoincrement=True)
    numero_encomenda      = Column(String(30), nullable=False, unique=True)
    id_cliente            = Column(
        Integer,
        ForeignKey("cliente.id_cliente", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    data_encomenda        = Column(Date, nullable=False)
    data_entrega_prevista = Column(Date, nullable=True)
    data_entrega_real     = Column(Date, nullable=True)
    status                = Column(String(30), nullable=False, default="PENDENTE")
    desconto_percentual   = Column(Numeric(5, 2),  nullable=False, default=0)
    valor_bruto           = Column(Numeric(12, 2), nullable=False, default=0)
    valor_liquido         = Column(Numeric(12, 2), nullable=False, default=0)
    observacoes           = Column(Text, nullable=True)

    # ✅ Relationships para resolver nomes no _serializar
    cliente = relationship("Cliente", lazy="joined")
    itens   = relationship("ItemEncomenda", lazy="joined",
                           cascade="all, delete-orphan")


class ItemEncomenda(Base):
    """Tabela associativa N:N — Encomenda ↔ Produto."""

    __tablename__ = "item_encomenda"

    id_item        = Column(Integer, primary_key=True, autoincrement=True)
    id_encomenda   = Column(
        Integer,
        ForeignKey("encomenda.id_encomenda", ondelete="CASCADE"),
        nullable=False,
    )
    id_produto     = Column(
        Integer,
        ForeignKey("produto.id_produto", ondelete="RESTRICT"),
        nullable=False,
    )
    quantidade     = Column(Integer,       nullable=False)
    preco_unitario = Column(Numeric(10,2), nullable=False)
    subtotal       = Column(Numeric(12,2), nullable=False)

    # ✅ Relationship para resolver nome do produto nos itens
    produto = relationship("Produto", lazy="joined")

    __table_args__ = (
        UniqueConstraint("id_encomenda", "id_produto", name="uq_enc_produto"),
    )
