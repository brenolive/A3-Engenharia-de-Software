"""Router: Produtos."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.produto import Produto, ProdutoComponente
from backend.schemas.produto import (
    ProdutoComponenteCreate,
    ProdutoComponenteResponse,
    ProdutoCreate,
    ProdutoResponse,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.post("/", response_model=ProdutoResponse, status_code=201)
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    if db.query(Produto).filter(Produto.codigo == dados.codigo).first():
        raise HTTPException(status_code=409, detail="Código já cadastrado.")

    p = Produto(**dados.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()


@router.get("/{id_produto}", response_model=ProdutoResponse)
def buscar_produto(id_produto: int, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return p


@router.delete("/{id_produto}", status_code=204)
def deletar_produto(id_produto: int, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    db.delete(p)
    db.commit()

# ── Atualizar produto ─────────────────────────────────────────

from backend.schemas.produto import ProdutoUpdate  # adicionar no topo do arquivo


@router.put("/{id_produto}", response_model=ProdutoResponse)
def atualizar_produto(
    id_produto: int,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db),
):
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    # Verifica conflito de código se foi alterado
    if dados.codigo and dados.codigo != p.codigo:
        if db.query(Produto).filter(Produto.codigo == dados.codigo).first():
            raise HTTPException(status_code=409, detail="Código já cadastrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(p, campo, valor)

    db.commit()
    db.refresh(p)
    return p


# ── Vínculos Produto ↔ Componente ────────────────────────────

@router.post(
    "/{id_produto}/componentes",
    response_model=ProdutoComponenteResponse,
    status_code=201,
)
def vincular_componente(
    id_produto: int,
    dados: ProdutoComponenteCreate,
    db: Session = Depends(get_db),
):
    existente = db.query(ProdutoComponente).filter(
        ProdutoComponente.id_produto == id_produto,
        ProdutoComponente.id_componente == dados.id_componente,
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Componente já vinculado.")

    pc = ProdutoComponente(
        id_produto=id_produto,
        id_componente=dados.id_componente,
        quantidade_necessaria=dados.quantidade_necessaria,
        unidade_medida=dados.unidade_medida,
        tempo_uso_horas=dados.tempo_uso_horas,
        observacao=dados.observacao,
    )
    db.add(pc)
    db.commit()
    db.refresh(pc)
    return pc


@router.get(
    "/{id_produto}/componentes",
    response_model=List[ProdutoComponenteResponse],
)
def listar_componentes_produto(id_produto: int, db: Session = Depends(get_db)):
    """Consulta: Produtos e seus componentes."""
    return db.query(ProdutoComponente).filter(
        ProdutoComponente.id_produto == id_produto
    ).all()
