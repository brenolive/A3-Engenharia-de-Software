"""Router: Fornecedores."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.fornecedor import Fornecedor, FornecedorComponente
from backend.schemas.fornecedor import (
    FornecedorComponenteCreate,
    FornecedorComponenteResponse,
    FornecedorCreate,
    FornecedorResponse,
    FornecedorUpdate,               # ← ADICIONADO
)
from backend.services.validacoes import validar_cnpj

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


@router.post("/", response_model=FornecedorResponse, status_code=201)
def criar_fornecedor(dados: FornecedorCreate, db: Session = Depends(get_db)):
    cnpj = validar_cnpj(dados.cnpj)
    if db.query(Fornecedor).filter(Fornecedor.cnpj == cnpj).first():
        raise HTTPException(status_code=409, detail="CNPJ já cadastrado.")

    f = Fornecedor(**{**dados.model_dump(), "cnpj": cnpj})
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@router.get("/", response_model=List[FornecedorResponse])
def listar_fornecedores(db: Session = Depends(get_db)):
    return db.query(Fornecedor).all()


@router.get("/{id_fornecedor}", response_model=FornecedorResponse)
def buscar_fornecedor(id_fornecedor: int, db: Session = Depends(get_db)):
    f = db.query(Fornecedor).filter(
        Fornecedor.id_fornecedor == id_fornecedor
    ).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")
    return f


@router.delete("/{id_fornecedor}", status_code=204)
def deletar_fornecedor(id_fornecedor: int, db: Session = Depends(get_db)):
    f = db.query(Fornecedor).filter(
        Fornecedor.id_fornecedor == id_fornecedor
    ).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")
    db.delete(f)
    db.commit()


@router.put("/{id_fornecedor}", response_model=FornecedorResponse)
def atualizar_fornecedor(
    id_fornecedor: int,
    dados: FornecedorUpdate,        # ← agora reconhecido
    db: Session = Depends(get_db),
):
    f = db.query(Fornecedor).filter(
        Fornecedor.id_fornecedor == id_fornecedor
    ).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")

    if dados.cnpj:
        cnpj_novo = validar_cnpj(dados.cnpj)
        if cnpj_novo != f.cnpj:
            if db.query(Fornecedor).filter(Fornecedor.cnpj == cnpj_novo).first():
                raise HTTPException(status_code=409, detail="CNPJ já cadastrado.")
            dados = dados.model_copy(update={"cnpj": cnpj_novo})

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(f, campo, valor)

    db.commit()
    db.refresh(f)
    return f


# ── Vínculos Fornecedor ↔ Componente ────────────────────────

@router.post(
    "/{id_fornecedor}/componentes",
    response_model=FornecedorComponenteResponse,
    status_code=201,
)
def vincular_componente(
    id_fornecedor: int,
    dados: FornecedorComponenteCreate,
    db: Session = Depends(get_db),
):
    existente = db.query(FornecedorComponente).filter(
        FornecedorComponente.id_fornecedor == id_fornecedor,
        FornecedorComponente.id_componente == dados.id_componente,
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Vínculo já existe.")

    fc = FornecedorComponente(
        id_fornecedor=id_fornecedor,
        id_componente=dados.id_componente,
        preco_unitario=dados.preco_unitario,
        prazo_entrega_dias=dados.prazo_entrega_dias,
        fornecedor_preferencial=dados.fornecedor_preferencial,
    )
    db.add(fc)
    db.commit()
    db.refresh(fc)
    return fc


@router.get(
    "/{id_fornecedor}/componentes",
    response_model=List[FornecedorComponenteResponse],
)
def listar_componentes_fornecedor(
    id_fornecedor: int, db: Session = Depends(get_db)
):
    return db.query(FornecedorComponente).filter(
        FornecedorComponente.id_fornecedor == id_fornecedor
    ).all()
