"""Schemas Pydantic — Cliente."""

import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


# ─────────────────────────────────────────────
#  Base interna (validadores compartilhados)
# ─────────────────────────────────────────────
class _ClienteValidadores(BaseModel):
    """Classe base privada que centraliza os validadores reutilizáveis."""

    @field_validator("cnpj", mode="before", check_fields=False)
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        digitos = re.sub(r"\D", "", v)
        if len(digitos) == 11:
            raise ValueError(
                "CPF não é aceito. O sistema atende apenas Pessoas Jurídicas (CNPJ)."
            )
        if len(digitos) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos.")
        return v

    @field_validator("razao_social", mode="before", check_fields=False)
    @classmethod
    def validar_razao(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Razão social deve ter ao menos 3 caracteres.")
        return v.strip()

    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def validar_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError("E-mail inválido.")
        return v.lower().strip()


# ─────────────────────────────────────────────
#  CREATE — todos os campos obrigatórios/opcionais como antes
# ─────────────────────────────────────────────
class ClienteCreate(_ClienteValidadores):
    """Payload para cadastro de novo cliente."""

    cnpj:          str
    razao_social:  str
    nome_fantasia: Optional[str] = None
    email:         str
    telefone:      Optional[str] = None
    cep:           Optional[str] = None
    logradouro:    Optional[str] = None
    numero:        Optional[str] = None
    complemento:   Optional[str] = None
    bairro:        Optional[str] = None
    cidade:        Optional[str] = None
    estado:        Optional[str] = None


# ─────────────────────────────────────────────
#  UPDATE — todos os campos opcionais (PATCH semântico via PUT)
#  ⚠️ CNPJ excluído: RN-02 — identificador único, não editável
# ─────────────────────────────────────────────
class ClienteUpdate(_ClienteValidadores):
    """Payload para atualização de cliente.

    Todos os campos são opcionais para permitir atualização parcial.
    CNPJ não pode ser alterado (RN-02).
    """

    razao_social:  Optional[str] = None
    nome_fantasia: Optional[str] = None
    email:         Optional[str] = None
    telefone:      Optional[str] = None
    cep:           Optional[str] = None
    logradouro:    Optional[str] = None
    numero:        Optional[str] = None
    complemento:   Optional[str] = None
    bairro:        Optional[str] = None
    cidade:        Optional[str] = None
    estado:        Optional[str] = None


# ─────────────────────────────────────────────
#  RESPONSE — retorno da API
# ─────────────────────────────────────────────
class ClienteResponse(BaseModel):
    """Schema de resposta — inclui campos gerados pelo banco."""

    id_cliente:    int
    cnpj:          str
    razao_social:  str
    nome_fantasia: Optional[str]
    email:         str
    telefone:      Optional[str]
    cep:           Optional[str]
    logradouro:    Optional[str]
    numero:        Optional[str]
    complemento:   Optional[str]
    bairro:        Optional[str]
    cidade:        Optional[str]
    estado:        Optional[str]
    data_cadastro: Optional[date]

    model_config = {"from_attributes": True}
