"""Schemas Pydantic — Encomenda."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, field_validator


# ============================================================
# ITEM
# ============================================================
class ItemEncomendaCreate(BaseModel):
    id_produto:     int
    quantidade:     int
    preco_unitario: float

    @field_validator("quantidade")
    @classmethod
    def qtd_positiva(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        return v

    @field_validator("preco_unitario")
    @classmethod
    def preco_nao_negativo(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Preço não pode ser negativo.")
        return v


class ItemEncomendaResponse(BaseModel):
    id_item:        int
    id_produto:     int
    produto_nome:   Optional[str]  = None   # ✅ nome do produto
    quantidade:     int
    preco_unitario: float
    subtotal:       float

    model_config = {"from_attributes": True}


# ============================================================
# ENCOMENDA
# ============================================================
class EncomendaCreate(BaseModel):
    id_cliente:            int
    data_entrega_prevista: Optional[date] = None
    desconto_percentual:   float          = 0.0
    observacoes:           Optional[str]  = None
    itens:                 List[ItemEncomendaCreate]

    @field_validator("desconto_percentual")
    @classmethod
    def desconto_valido(cls, v: float) -> float:
        if not (0 <= v <= 100):
            raise ValueError("Desconto deve estar entre 0 e 100.")
        return v

    @field_validator("itens")
    @classmethod
    def ao_menos_um_item(cls, v):
        if not v:
            raise ValueError("A encomenda deve ter ao menos um item.")
        return v


class EncomendaResponse(BaseModel):
    id_encomenda:          int
    numero_encomenda:      str
    id_cliente:            int
    cliente_nome:          Optional[str]             = None  # ✅ nome do cliente
    data_encomenda:        date
    data_entrega_prevista: Optional[date]            = None
    status:                str
    desconto_percentual:   float
    valor_bruto:           float
    valor_liquido:         float
    observacoes:           Optional[str]             = None
    itens:                 List[ItemEncomendaResponse] = []  # ✅ itens com nome

    model_config = {"from_attributes": True}
