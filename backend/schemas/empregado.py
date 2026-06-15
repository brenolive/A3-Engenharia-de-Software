"""Schemas Pydantic — Empregado."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class EmpregadoCreate(BaseModel):
    matricula:     str
    nome:          str
    cpf:           str
    email:         Optional[str]  = None
    telefone:      Optional[str]  = None
    cep:           Optional[str]  = None
    logradouro:    Optional[str]  = None
    numero:        Optional[str]  = None
    complemento:   Optional[str]  = None
    bairro:        Optional[str]  = None
    cidade:        Optional[str]  = None
    estado:        Optional[str]  = None
    cargo:         str
    salario:       float
    data_admissao: date
    qualificacoes: Optional[str]  = None
    id_supervisor: Optional[int]  = None


class EmpregadoResponse(BaseModel):
    id_empregado:    int
    matricula:       str
    nome:            str
    cpf:             str
    email:           Optional[str]  = None
    telefone:        Optional[str]  = None
    cargo:           str
    salario:         float
    data_admissao:   date
    qualificacoes:   Optional[str]  = None
    id_supervisor:   Optional[int]  = None
    supervisor_nome: Optional[str]  = None  # ✅ resolvido pelo router

    model_config = {"from_attributes": True}


class EmpregadoUpdate(BaseModel):
    matricula:     Optional[str]   = None
    nome:          Optional[str]   = None
    cpf:           Optional[str]   = None
    cargo:         Optional[str]   = None
    salario:       Optional[float] = None
    data_admissao: Optional[date]  = None   # ✅ date, não str
    email:         Optional[str]   = None
    telefone:      Optional[str]   = None
    id_supervisor: Optional[int]   = None
    qualificacoes: Optional[str]   = None   # ✅ igual ao model

    model_config = {"from_attributes": True}
