"""Schemas Pydantic — Produto."""

from typing import Optional
from pydantic import BaseModel


class ProdutoCreate(BaseModel):
    codigo:         str
    nome:           str
    descricao:      Optional[str]   = None
    preco_unitario: float
    categoria:      Optional[str]   = None
    ativo:          bool            = True


class ProdutoResponse(BaseModel):
    id_produto:     int
    codigo:         str
    nome:           str
    descricao:      Optional[str]
    preco_unitario: float
    categoria:      Optional[str]
    ativo:          bool

    model_config = {"from_attributes": True}


class ProdutoComponenteCreate(BaseModel):
    id_produto:            int
    id_componente:         int
    quantidade_necessaria: float
    unidade_medida:        str   = "un"
    tempo_uso_horas:       Optional[float] = None
    observacao:            Optional[str]   = None


class ProdutoComponenteResponse(ProdutoComponenteCreate):
    id_prod_comp: int

    model_config = {"from_attributes": True}


class ProdutoUpdate(BaseModel):
    codigo:    Optional[str]   = None
    nome:      Optional[str]   = None
    descricao: Optional[str]   = None
    preco:     Optional[float] = None
    categoria: Optional[str]   = None
    ativo:     Optional[bool]  = None

    model_config = {"from_attributes": True}