"""Model: Registro de Manutenção de Máquinas."""

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text
from backend.database import Base


class Manutencao(Base):
    __tablename__ = "manutencao"

    id_manutencao       = Column(Integer, primary_key=True, autoincrement=True)
    id_componente       = Column(
        Integer,
        ForeignKey("maquina.id_componente", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    id_empresa_manut    = Column(
        Integer,
        ForeignKey("empresa_manutencao.id_empresa_manut", ondelete="RESTRICT"),
        nullable=False,
    )
    tipo_manutencao     = Column(String(30), nullable=False)
    data_inicio         = Column(Date, nullable=False)
    data_fim            = Column(Date, nullable=True)
    custo               = Column(Numeric(10, 2), nullable=True)
    descricao           = Column(Text, nullable=True)
    pecas_substituidas  = Column(Text, nullable=True)
    responsavel_interno = Column(String(150), nullable=True)
