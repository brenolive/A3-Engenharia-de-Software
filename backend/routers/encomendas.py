"""Router: Encomendas."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.encomenda import Encomenda, ItemEncomenda
from backend.schemas.encomenda import (
    EncomendaCreate,
    EncomendaResponse,
    ItemEncomendaResponse,
)
from backend.services.encomenda_service import criar_encomenda

router = APIRouter(prefix="/encomendas", tags=["Encomendas"])


# ============================================================
# HELPER — converte ORM → Response com cliente_nome e itens
# ============================================================
def _serializar(enc: Encomenda) -> EncomendaResponse:
    """Monta EncomendaResponse resolvendo cliente_nome e itens."""

    # ── Nome do cliente ──────────────────────────────────────
    cliente_nome = None
    if enc.cliente:
        cliente_nome = (
            getattr(enc.cliente, "nome_fantasia", None)
            or getattr(enc.cliente, "razao_social", None)
            or getattr(enc.cliente, "nome", None)
        )

    # ── Itens com nome do produto ────────────────────────────
    itens_resp = []
    for item in (enc.itens or []):
        produto_nome = None
        if item.produto:
            produto_nome = getattr(item.produto, "nome", None)

        itens_resp.append(ItemEncomendaResponse(
            id_item        = item.id_item,
            id_produto     = item.id_produto,
            produto_nome   = produto_nome,
            quantidade     = item.quantidade,
            preco_unitario = float(item.preco_unitario),
            subtotal       = float(item.subtotal),
        ))

    return EncomendaResponse(
        id_encomenda          = enc.id_encomenda,
        numero_encomenda      = enc.numero_encomenda,
        id_cliente            = enc.id_cliente,
        cliente_nome          = cliente_nome,
        data_encomenda        = enc.data_encomenda,
        data_entrega_prevista = enc.data_entrega_prevista,
        status                = enc.status,
        desconto_percentual   = float(enc.desconto_percentual),
        valor_bruto           = float(enc.valor_bruto),
        valor_liquido         = float(enc.valor_liquido),
        observacoes           = enc.observacoes,
        itens                 = itens_resp,
    )


# ============================================================
# POST — Criar encomenda
# ============================================================
@router.post("/", response_model=EncomendaResponse, status_code=201)
def nova_encomenda(dados: EncomendaCreate, db: Session = Depends(get_db)):
    enc = criar_encomenda(dados, db)
    # ✅ Recarrega via db.get() para garantir que relationships
    #    cliente e itens estejam populados após o commit
    enc = db.get(Encomenda, enc.id_encomenda)
    return _serializar(enc)


# ============================================================
# GET — Listar todas
# ============================================================
@router.get("/", response_model=List[EncomendaResponse])
def listar_encomendas(db: Session = Depends(get_db)):
    encomendas = db.query(Encomenda).all()
    return [_serializar(e) for e in encomendas]


# ============================================================
# GET — Por cliente
# ============================================================
@router.get("/cliente/{id_cliente}", response_model=List[EncomendaResponse])
def encomendas_por_cliente(id_cliente: int, db: Session = Depends(get_db)):
    encomendas = db.query(Encomenda).filter(
        Encomenda.id_cliente == id_cliente
    ).all()
    return [_serializar(e) for e in encomendas]


# ============================================================
# GET — Por ID
# ============================================================
@router.get("/{id_encomenda}", response_model=EncomendaResponse)
def buscar_encomenda(id_encomenda: int, db: Session = Depends(get_db)):
    enc = db.get(Encomenda, id_encomenda)
    if not enc:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada.")
    return _serializar(enc)


# ============================================================
# PATCH — Atualizar status
# ============================================================
@router.patch("/{id_encomenda}/status", response_model=EncomendaResponse)
def atualizar_status(
    id_encomenda: int,
    status: str,
    db: Session = Depends(get_db),
):
    STATUS_VALIDOS = {"PENDENTE", "EM_PRODUCAO", "ENTREGUE", "CANCELADA"}
    if status not in STATUS_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Status inválido. Use: {STATUS_VALIDOS}",
        )
    enc = db.get(Encomenda, id_encomenda)
    if not enc:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada.")
    enc.status = status
    db.commit()
    db.refresh(enc)
    return _serializar(enc)


# ============================================================
# DELETE — Excluir encomenda
# ============================================================
@router.delete("/{id_encomenda}", status_code=204)
def deletar_encomenda(id_encomenda: int, db: Session = Depends(get_db)):
    enc = db.get(Encomenda, id_encomenda)
    if not enc:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada.")
    db.delete(enc)
    db.commit()
