"""
Testes: Encomendas
CT-02 — Encomenda com desconto
CT-06 — Múltiplos produtos
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

TEST_URL = "sqlite:///./test_enc.db"
engine_test = create_engine(TEST_URL, connect_args={"check_same_thread": False})
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.clear()


client = TestClient(app)


def criar_cliente() -> int:
    resp = client.post("/clientes/", json={
        "cnpj":         "11.222.333/0001-81",
        "razao_social": "Cliente Teste LTDA",
        "email":        "cli@teste.com",
    })
    return resp.json()["id_cliente"]


def criar_produto(codigo: str, preco: float) -> int:
    resp = client.post("/produtos/", json={
        "codigo":         codigo,
        "nome":           f"Produto {codigo}",
        "preco_unitario": preco,
    })
    return resp.json()["id_produto"]


# ── CT-02 ────────────────────────────────────────────────────
def test_ct02_encomenda_com_desconto():
    """
    CT-02: 5 unidades × R$800 com 10% de desconto.
    Bruto: R$4000 | Líquido: R$3600
    """
    id_cli  = criar_cliente()
    id_prod = criar_produto("MESA-001", 800.0)

    resp = client.post("/encomendas/", json={
        "id_cliente":          id_cli,
        "desconto_percentual": 10,
        "itens": [
            {"id_produto": id_prod, "quantidade": 5, "preco_unitario": 800.0}
        ],
    })

    assert resp.status_code == 201
    data = resp.json()
    assert float(data["valor_bruto"])   == 4000.0
    assert float(data["valor_liquido"]) == 3600.0
    assert data["numero_encomenda"].startswith("ENC-")
    assert data["status"] == "PENDENTE"


# ── CT-06: Múltiplos produtos ────────────────────────────────
def test_ct06_multiplos_produtos():
    """
    CT-06: 3 produtos distintos com 5% de desconto.
    Bruto: R$3100 | Líquido: R$2945
    """
    id_cli  = criar_cliente()
    id_p1   = criar_produto("PROD-A", 500.0)
    id_p2   = criar_produto("PROD-B", 1200.0)
    id_p3   = criar_produto("PROD-C", 300.0)

    resp = client.post("/encomendas/", json={
        "id_cliente":          id_cli,
        "desconto_percentual": 5,
        "itens": [
            {"id_produto": id_p1, "quantidade": 2,  "preco_unitario": 500.0},
            {"id_produto": id_p2, "quantidade": 1,  "preco_unitario": 1200.0},
            {"id_produto": id_p3, "quantidade": 3,  "preco_unitario": 300.0},
        ],
    })

    assert resp.status_code == 201
    data = resp.json()
    assert float(data["valor_bruto"])   == 3100.0
    assert float(data["valor_liquido"]) == 2945.0


def test_encomenda_cliente_inexistente():
    """Encomenda com cliente inexistente deve retornar 404."""
    criar_produto("PROD-X", 100.0)
    resp = client.post("/encomendas/", json={
        "id_cliente": 9999,
        "itens": [{"id_produto": 1, "quantidade": 1, "preco_unitario": 100.0}],
    })
    assert resp.status_code == 404


def test_encomenda_sem_itens():
    """Encomenda sem itens deve retornar 422."""
    id_cli = criar_cliente()
    resp = client.post("/encomendas/", json={
        "id_cliente": id_cli,
        "itens": [],
    })
    assert resp.status_code == 422


def test_desconto_invalido():
    """Desconto acima de 100% deve retornar 422."""
    id_cli  = criar_cliente()
    id_prod = criar_produto("PROD-Y", 100.0)
    resp = client.post("/encomendas/", json={
        "id_cliente":          id_cli,
        "desconto_percentual": 150,
        "itens": [{"id_produto": id_prod, "quantidade": 1, "preco_unitario": 100.0}],
    })
    assert resp.status_code == 422
