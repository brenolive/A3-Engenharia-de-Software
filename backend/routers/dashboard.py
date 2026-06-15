from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from backend.database import get_db
from backend.models.encomenda import Encomenda, ItemEncomenda
from backend.models.cliente import Cliente
from backend.models.produto import Produto
from backend.models.componente import Maquina
from backend.models.empregado import Empregado
from backend.models.fornecedor import Fornecedor

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/totais")
def get_totais(db: Session = Depends(get_db)):

    # ── Totais básicos ───────────────────────────────────────
    total_clientes   = db.query(func.count(Cliente.id_cliente)).scalar()
    total_produtos   = db.query(func.count(Produto.id_produto)).scalar()
    total_encomendas = db.query(func.count(Encomenda.id_encomenda)).scalar()
    total_empregados = db.query(func.count(Empregado.id_empregado)).scalar()
    total_fornecedores = db.query(func.count(Fornecedor.id_fornecedor)).scalar()
    total_componentes  = db.query(func.count(Produto.id_produto)).scalar()

    # ── Faturamento ──────────────────────────────────────────
    faturamento_bruto = float(
        db.query(func.sum(Encomenda.valor_bruto)).scalar() or 0
    )
    faturamento_liq = float(
        db.query(func.sum(Encomenda.valor_liquido)).scalar() or 0
    )

    # ── Máquinas em manutenção ───────────────────────────────
    maquinas_manutencao = db.query(
        func.count(Maquina.id_componente)
    ).filter(Maquina.em_manutencao == True).scalar()

    # ── Encomendas por status ────────────────────────────────
    pendentes   = db.query(func.count(Encomenda.id_encomenda)).filter(
        Encomenda.status == "PENDENTE").scalar()
    em_producao = db.query(func.count(Encomenda.id_encomenda)).filter(
        Encomenda.status == "EM_PRODUCAO").scalar()
    entregues   = db.query(func.count(Encomenda.id_encomenda)).filter(
        Encomenda.status == "ENTREGUE").scalar()
    canceladas  = db.query(func.count(Encomenda.id_encomenda)).filter(
        Encomenda.status == "CANCELADA").scalar()

    # ── Encomendas dos últimos 30 dias ───────────────────────
    data_30d = date.today() - timedelta(days=30)
    enc_30d  = db.query(func.count(Encomenda.id_encomenda)).filter(
        Encomenda.data_encomenda >= data_30d
    ).scalar()

    fat_30d = float(
        db.query(func.sum(Encomenda.valor_liquido)).filter(
            Encomenda.data_encomenda >= data_30d
        ).scalar() or 0
    )

    # ── Entregas no prazo vs atrasadas ───────────────────────
    # Encomendas ENTREGUE com data_entrega_real <= data_entrega_prevista
    no_prazo = db.query(func.count(Encomenda.id_encomenda)).filter(
        Encomenda.status == "ENTREGUE",
        Encomenda.data_entrega_prevista != None,
        Encomenda.data_entrega_real     != None,
        Encomenda.data_entrega_real     <= Encomenda.data_entrega_prevista,
    ).scalar()

    atrasadas = db.query(func.count(Encomenda.id_encomenda)).filter(
        Encomenda.status == "ENTREGUE",
        Encomenda.data_entrega_prevista != None,
        Encomenda.data_entrega_real     != None,
        Encomenda.data_entrega_real     > Encomenda.data_entrega_prevista,
    ).scalar()

    # ── Produto mais vendido ─────────────────────────────────
    prod_mais_vendido = (
        db.query(
            Produto.nome,
            func.sum(ItemEncomenda.quantidade).label("qtd_total"),
            func.sum(ItemEncomenda.subtotal).label("receita"),
        )
        .join(ItemEncomenda, ItemEncomenda.id_produto == Produto.id_produto)
        .group_by(Produto.id_produto)
        .order_by(func.sum(ItemEncomenda.quantidade).desc())
        .first()
    )

    # ── Top 5 clientes por faturamento ───────────────────────
    top_clientes = (
        db.query(
            Cliente.razao_social,
            Cliente.nome_fantasia,
            func.sum(Encomenda.valor_liquido).label("total"),
            func.count(Encomenda.id_encomenda).label("qtd"),
        )
        .join(Encomenda, Encomenda.id_cliente == Cliente.id_cliente)
        .group_by(Cliente.id_cliente)
        .order_by(func.sum(Encomenda.valor_liquido).desc())
        .limit(5)
        .all()
    )

    # ── Últimas 8 encomendas ─────────────────────────────────
    ultimas = (
        db.query(Encomenda, Cliente.razao_social, Cliente.nome_fantasia)
        .join(Cliente, Cliente.id_cliente == Encomenda.id_cliente)
        .order_by(Encomenda.id_encomenda.desc())
        .limit(8)
        .all()
    )

    # ── Encomendas em produção (detalhes) ────────────────────
    em_prod_detalhe = (
        db.query(Encomenda, Cliente.razao_social, Cliente.nome_fantasia)
        .join(Cliente, Cliente.id_cliente == Encomenda.id_cliente)
        .filter(Encomenda.status == "EM_PRODUCAO")
        .order_by(Encomenda.data_entrega_prevista.asc().nullslast())
        .limit(5)
        .all()
    )

    # ── Encomendas canceladas (detalhes) ─────────────────────
    canceladas_detalhe = (
        db.query(Encomenda, Cliente.razao_social, Cliente.nome_fantasia)
        .join(Cliente, Cliente.id_cliente == Encomenda.id_cliente)
        .filter(Encomenda.status == "CANCELADA")
        .order_by(Encomenda.id_encomenda.desc())
        .limit(5)
        .all()
    )

    # ── Faturamento mensal — bruto e líquido ─────────────────
    fat_por_mes = (
        db.query(
            func.strftime("%Y-%m", Encomenda.data_encomenda).label("mes"),
            func.sum(Encomenda.valor_bruto).label("bruto"),
            func.sum(Encomenda.valor_liquido).label("total"),
            func.count(Encomenda.id_encomenda).label("qtd"),
        )
        .group_by(func.strftime("%Y-%m", Encomenda.data_encomenda))
        .order_by(func.strftime("%Y-%m", Encomenda.data_encomenda))
        .all()
    )

    # ── Top 5 produtos por receita ────────────────────────────
    top_produtos = (
        db.query(
            Produto.nome,
            func.sum(ItemEncomenda.quantidade).label("qtd_total"),
            func.sum(ItemEncomenda.subtotal).label("receita"),
        )
        .join(ItemEncomenda, ItemEncomenda.id_produto == Produto.id_produto)
        .group_by(Produto.id_produto)
        .order_by(func.sum(ItemEncomenda.subtotal).desc())
        .limit(5)
        .all()
    )

    # ── Helper nome cliente ───────────────────────────────────
    def nome_cliente(razao, fantasia):
        return fantasia or razao or "—"

    return {
        # KPIs básicos
        "clientes":             total_clientes,
        "produtos":             total_produtos,
        "encomendas":           total_encomendas,
        "empregados":           total_empregados,
        "fornecedores":         total_fornecedores,
        "componentes":          total_componentes,
        "faturamento_bruto":    round(faturamento_bruto, 2),
        "faturamento_liquido":  round(faturamento_liq, 2),
        "maquinas_manutencao":  maquinas_manutencao,

        # Últimos 30 dias
        "ultimos_30_dias": {
            "encomendas":  enc_30d,
            "faturamento": round(fat_30d, 2),
        },

        # Status
        "status": {
            "pendentes":   pendentes,
            "em_producao": em_producao,
            "entregues":   entregues,
            "canceladas":  canceladas,
        },

        # Entregas
        "entregas": {
            "no_prazo":  no_prazo,
            "atrasadas": atrasadas,
        },

        # Produto mais vendido
        "produto_mais_vendido": {
            "nome":    prod_mais_vendido.nome            if prod_mais_vendido else None,
            "qtd":     int(prod_mais_vendido.qtd_total)  if prod_mais_vendido else 0,
            "receita": round(float(prod_mais_vendido.receita), 2) if prod_mais_vendido else 0,
        },

        # Top clientes
        "top_clientes": [
            {
                "nome":  nome_cliente(r.nome_fantasia, r.razao_social),
                "total": round(float(r.total), 2),
                "qtd":   r.qtd,
            }
            for r in top_clientes
        ],

        # Top produtos
        "top_produtos": [
            {
                "nome":    r.nome,
                "qtd":     int(r.qtd_total),
                "receita": round(float(r.receita), 2),
            }
            for r in top_produtos
        ],

        # Últimas encomendas
        "ultimas_encomendas": [
            {
                "numero":  enc.numero_encomenda,
                "cliente": nome_cliente(fantasia, razao),
                "valor":   round(float(enc.valor_liquido), 2),
                "status":  enc.status,
                "data":    str(enc.data_encomenda),
            }
            for enc, razao, fantasia in ultimas
        ],

        # Em produção
        "em_producao_detalhe": [
            {
                "numero":   enc.numero_encomenda,
                "cliente":  nome_cliente(fantasia, razao),
                "valor":    round(float(enc.valor_liquido), 2),
                "entrega":  str(enc.data_entrega_prevista) if enc.data_entrega_prevista else "—",
            }
            for enc, razao, fantasia in em_prod_detalhe
        ],

        # Canceladas
        "canceladas_detalhe": [
            {
                "numero":  enc.numero_encomenda,
                "cliente": nome_cliente(fantasia, razao),
                "valor":   round(float(enc.valor_liquido), 2),
                "data":    str(enc.data_encomenda),
            }
            for enc, razao, fantasia in canceladas_detalhe
        ],

        # Faturamento mensal
        "faturamento_mensal": [
            {
                "mes":   r.mes,
                "bruto": round(float(r.bruto), 2),
                "total": round(float(r.total), 2),
                "qtd":   r.qtd,
            }
            for r in fat_por_mes
        ],
    }
