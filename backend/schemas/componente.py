"""Schemas Pydantic — Componente e Especializações."""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel


TIPOS_COMPONENTE = Literal[
    "MATERIA_PRIMA", "MATERIAL_DIVERSO", "MAQUINA", "FERRAMENTA"
]


class ComponenteCreate(BaseModel):
    nome:            str
    descricao:       Optional[str] = None
    tipo_componente: TIPOS_COMPONENTE
    # Campos de MateriaPrima
    origem:          Optional[str] = None
    tipo_madeira:    Optional[str] = None
    certificacao:    Optional[str] = None
    # Campos de MaterialDiverso
    categoria:       Optional[str] = None
    marca:           Optional[str] = None
    # Campos de Maquina
    modelo:            Optional[str]  = None
    fabricante:        Optional[str]  = None
    numero_serie:      Optional[str]  = None
    tempo_medio_vida:  Optional[int]  = None
    data_compra:       Optional[date] = None
    data_fim_garantia: Optional[date] = None
    # Campos de Ferramenta
    tipo_ferramenta: Optional[str] = None
    # marca e numero_serie já declarados acima


class ComponenteResponse(BaseModel):
    id_componente:   int
    nome:            str
    descricao:       Optional[str]
    tipo_componente: str

    model_config = {"from_attributes": True}

class ComponenteUpdate(BaseModel):
    # Campos base
    nome:        Optional[str] = None
    descricao:   Optional[str] = None

    # MateriaPrima
    origem:        Optional[str] = None
    tipo_madeira:  Optional[str] = None
    certificacao:  Optional[str] = None

    # MaterialDiverso
    categoria: Optional[str] = None

    # Maquina
    modelo:            Optional[str]  = None
    fabricante:        Optional[str]  = None
    numero_serie:      Optional[str]  = None
    tempo_medio_vida:  Optional[int]  = None
    data_compra:       Optional[str]  = None
    data_fim_garantia: Optional[str]  = None

    # Ferramenta
    tipo_ferramenta: Optional[str] = None

    # Compartilhado (MaterialDiverso + Ferramenta)
    marca: Optional[str] = None

    model_config = {"from_attributes": True}
