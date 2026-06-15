"""Model: Empregado com auto-relacionamento de supervisão."""

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text
from backend.database import Base


class Empregado(Base):
    __tablename__ = "empregado"

    id_empregado  = Column(Integer, primary_key=True, autoincrement=True)
    matricula     = Column(String(20),    nullable=False, unique=True)
    nome          = Column(String(150),   nullable=False)
    cpf           = Column(String(14),    nullable=False, unique=True)
    email         = Column(String(100),   nullable=True)
    telefone      = Column(String(20),    nullable=True)
    cep           = Column(String(10),    nullable=True)
    logradouro    = Column(String(150),   nullable=True)
    numero        = Column(String(10),    nullable=True)
    complemento   = Column(String(50),    nullable=True)
    bairro        = Column(String(80),    nullable=True)
    cidade        = Column(String(80),    nullable=True)
    estado        = Column(String(2),     nullable=True)
    cargo         = Column(String(80),    nullable=False)
    salario       = Column(Numeric(10,2), nullable=False)
    data_admissao = Column(Date,          nullable=False)
    qualificacoes = Column(Text,          nullable=True)

    id_supervisor = Column(
        Integer,
        ForeignKey("empregado.id_empregado", ondelete="SET NULL"),
        nullable=True,
    )
