"""Schemas Pydantic — Fornecedor."""

from typing import Optional
from pydantic import BaseModel


class FornecedorCreate(BaseModel):
    cnpj:          str
    razao_social:  str
    nome_fantasia: Optional[str] = None
    email:         Optional[str] = None
    telefone:      Optional[str] = None
    cep:           Optional[str] = None
    logradouro:    Optional[str] = None
    numero:        Optional[str] = None
    bairro:        Optional[str] = None
    cidade:        Optional[str] = None
    estado:        Optional[str] = None


class FornecedorResponse(BaseModel):
    id_fornecedor: int
    cnpj:          str
    razao_social:  str
    nome_fantasia: Optional[str]
    email:         Optional[str]
    telefone:      Optional[str]
    cidade:        Optional[str]
    estado:        Optional[str]

    model_config = {"from_attributes": True}


class FornecedorComponenteCreate(BaseModel):
    id_fornecedor:          int
    id_componente:          int
    preco_unitario:         Optional[float] = None
    prazo_entrega_dias:     Optional[int]   = None
    fornecedor_preferencial: bool           = False


class FornecedorComponenteResponse(FornecedorComponenteCreate):
    id_forn_comp: int

    model_config = {"from_attributes": True}

class FornecedorUpdate(BaseModel):
    cnpj:          Optional[str] = None
    razao_social:  Optional[str] = None
    nome_fantasia: Optional[str] = None
    email:         Optional[str] = None
    telefone:      Optional[str] = None
    cidade:        Optional[str] = None
    estado:        Optional[str] = None

    model_config = {"from_attributes": True}