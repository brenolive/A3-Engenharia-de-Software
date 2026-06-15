"""Model: Empresa de Manutenção."""

from sqlalchemy import Column, Integer, String
from backend.database import Base


class EmpresaManutencao(Base):
    __tablename__ = "empresa_manutencao"

    id_empresa_manut = Column(Integer, primary_key=True, autoincrement=True)
    cnpj             = Column(String(18), nullable=False, unique=True)
    razao_social     = Column(String(150), nullable=False)
    nome_fantasia    = Column(String(150), nullable=True)
    email            = Column(String(100), nullable=True)
    telefone         = Column(String(20), nullable=True)
    especialidade    = Column(String(150), nullable=True)
