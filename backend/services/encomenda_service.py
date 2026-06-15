"""
Serviço de Encomendas — Orquestra regras de negócio.
"""

from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.cliente import Cliente
from backend.models.encomenda import Encomenda, ItemEncomenda
from backend.models.produto import Produto
from backend.schemas.encomenda import EncomendaCreate
from backend.services.validacoes import (
    calcular_valores_encomenda,
    gerar_numero_encomenda,
)


def criar_encomenda(dados: EncomendaCreate, db: Session) -> Encomenda:
    """
    Orquestra a criação de uma encomenda:
    1. Valida cliente
    2. Valida e coleta produtos
    3. Calcula valores
    4. Gera número
    5. Persiste encomenda e itens
    """
    # 1. Valida cliente
    cliente = db.query(Cliente).filter(
        Cliente.id_cliente == dados.id_cliente
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # 2. Valida produtos e monta itens
    itens_processados = []
    for item in dados.itens:
        produto = db.query(Produto).filter(
            Produto.id_produto == item.id_produto,
            Produto.ativo == True,  # noqa: E712
        ).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto ID {item.id_produto} não encontrado ou inativo.",
            )
        itens_processados.append(
            {
                "id_produto":     item.id_produto,
                "quantidade":     item.quantidade,
                "preco_unitario": float(item.preco_unitario),
                "subtotal":       round(item.quantidade * item.preco_unitario, 2),
            }
        )

    # 3. Calcula valores
    valores = calcular_valores_encomenda(
        itens_processados, float(dados.desconto_percentual)
    )

    # 4. Gera número da encomenda
    ultimo = (
        db.query(Encomenda).order_by(Encomenda.id_encomenda.desc()).first()
    )
    ultimo_id = ultimo.id_encomenda if ultimo else 0
    numero = gerar_numero_encomenda(ultimo_id)

    # 5. Persiste
    encomenda = Encomenda(
        numero_encomenda=numero,
        id_cliente=dados.id_cliente,
        data_encomenda=date.today(),
        data_entrega_prevista=dados.data_entrega_prevista,
        status="PENDENTE",
        desconto_percentual=dados.desconto_percentual,
        valor_bruto=valores["valor_bruto"],
        valor_liquido=valores["valor_liquido"],
        observacoes=dados.observacoes,
    )
    db.add(encomenda)
    db.flush()  # Garante id_encomenda antes de criar itens

    for item in itens_processados:
        db.add(
            ItemEncomenda(
                id_encomenda=encomenda.id_encomenda,
                id_produto=item["id_produto"],
                quantidade=item["quantidade"],
                preco_unitario=item["preco_unitario"],
                subtotal=item["subtotal"],
            )
        )

    db.commit()
    db.refresh(encomenda)
    return encomenda
