"""
Model: Componente (Generalização) + Especializações.
Padrão: Tabela por Hierarquia (STI) com discriminador tipo_componente.
"""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from backend.database import Base


class Componente(Base):
    __tablename__ = "componente"

    id_componente   = Column(Integer, primary_key=True, autoincrement=True)
    nome            = Column(String(150), nullable=False)
    descricao       = Column(Text, nullable=True)
    tipo_componente = Column(String(30), nullable=False)
    # Discriminador: MATERIA_PRIMA | MATERIAL_DIVERSO | MAQUINA | FERRAMENTA


class MateriaPrima(Base):
    __tablename__ = "materia_prima"

    id_componente = Column(
        Integer,
        ForeignKey("componente.id_componente", ondelete="CASCADE"),
        primary_key=True,
    )
    origem       = Column(String(100), nullable=True)
    tipo_madeira = Column(String(80), nullable=True)
    certificacao = Column(String(80), nullable=True)


class MaterialDiverso(Base):
    __tablename__ = "material_diverso"

    id_componente = Column(
        Integer,
        ForeignKey("componente.id_componente", ondelete="CASCADE"),
        primary_key=True,
    )
    categoria = Column(String(80), nullable=True)
    marca     = Column(String(80), nullable=True)


class Maquina(Base):
    __tablename__ = "maquina"

    id_componente     = Column(
        Integer,
        ForeignKey("componente.id_componente", ondelete="CASCADE"),
        primary_key=True,
    )
    modelo            = Column(String(100), nullable=True)
    fabricante        = Column(String(100), nullable=True)
    numero_serie      = Column(String(80), nullable=True)
    tempo_medio_vida  = Column(Integer, nullable=True)      # Em meses
    data_compra       = Column(Date, nullable=True)
    data_fim_garantia = Column(Date, nullable=True)
    em_manutencao     = Column(Boolean, nullable=False, default=False)


class Ferramenta(Base):
    __tablename__ = "ferramenta"

    id_componente   = Column(
        Integer,
        ForeignKey("componente.id_componente", ondelete="CASCADE"),
        primary_key=True,
    )
    tipo_ferramenta = Column(String(80), nullable=True)
    marca           = Column(String(80), nullable=True)
    numero_serie    = Column(String(80), nullable=True)
