"""Schemas Pydantic — Manutenção e Empresa de Manutenção."""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, field_validator


TIPOS_MANUTENCAO = Literal["PREVENTIVA", "CORRETIVA", "TROCA_PECAS"]


class EmpresaManutencaoCreate(BaseModel):
    cnpj:          str
    razao_social:  str
    nome_fantasia: Optional[str] = None
    email:         Optional[str] = None
    telefone:      Optional[str] = None
    especialidade: Optional[str] = None


class EmpresaManutencaoResponse(EmpresaManutencaoCreate):
    id_empresa_manut: int

    model_config = {"from_attributes": True}


class ManutencaoCreate(BaseModel):
    id_componente:      int
    id_empresa_manut:   int
    tipo_manutencao:    TIPOS_MANUTENCAO
    data_inicio:        date
    data_fim:           Optional[date]  = None
    custo:              Optional[float] = None
    descricao:          Optional[str]   = None
    pecas_substituidas: Optional[str]   = None
    responsavel_interno: Optional[str]  = None

    @field_validator("data_fim")
    @classmethod
    def data_fim_valida(cls, v, info):
        data_inicio = info.data.get("data_inicio")
        if v and data_inicio and v < data_inicio:
            raise ValueError("Data de conclusão não pode ser anterior à data de início.")
        return v


class ManutencaoResponse(BaseModel):
    id_manutencao:      int
    id_componente:      int
    id_empresa_manut:   int
    tipo_manutencao:    str
    data_inicio:        date
    data_fim:           Optional[date]
    custo:              Optional[float]
    descricao:          Optional[str]
    pecas_substituidas: Optional[str]
    responsavel_interno: Optional[str]
    componente_nome: Optional[str] = None
    empresa_nome:    Optional[str] = None

    model_config = {"from_attributes": True}
