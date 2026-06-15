"""
Testes: Clientes
CT-01 — Bloqueio de CPF
CT-10 — Campos obrigatórios
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

# Banco em memória para testes
TEST_URL = "sqlite:///./test_temp.db"
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

CLIENTE_VALIDO = {
    "cnpj":         "11.222.333/0001-81",
    "razao_social": "Empresa Teste LTDA",
    "email":        "contato@teste.com",
}


# ── CT-01: Bloqueio de CPF ───────────────────────────────────
def test_ct01_cpf_bloqueado():
    """CT-01: Sistema deve rejeitar CPF (apenas CNPJ aceito)."""
    resp = client.post("/clientes/", json={
        "cnpj":         "123.456.789-09",  # CPF
        "razao_social": "Pessoa Física Teste",
        "email":        "pf@teste.com",
    })
    assert resp.status_code == 422
    body = resp.json()
    # Pydantic retorna erro de validação
    assert any(
        "CPF" in str(e.get("msg", "")) or "PJ" in str(e.get("msg", ""))
        for e in body.get("detail", [{}])
    )


def test_ct01_cnpj_invalido_menos_14_digitos():
    """CT-01b: CNPJ com menos de 14 dígitos deve ser rejeitado."""
    resp = client.post("/clientes/", json={
        "cnpj": "12.345.678/0001",
        "razao_social": "Teste",
        "email": "x@x.com",
    })
    assert resp.status_code == 422


# ── CT-02: Cadastro válido ───────────────────────────────────
def test_cadastro_cliente_valido():
    """Cadastro com CNPJ válido deve retornar 201."""
    resp = client.post("/clientes/", json=CLIENTE_VALIDO)
    assert resp.status_code == 201
    data = resp.json()
    assert data["razao_social"] == "Empresa Teste LTDA"
    assert "id_cliente" in data


def test_cnpj_duplicado():
    """Segundo cadastro com mesmo CNPJ deve retornar 409."""
    client.post("/clientes/", json=CLIENTE_VALIDO)
    resp = client.post("/clientes/", json={**CLIENTE_VALIDO, "email": "outro@email.com"})
    assert resp.status_code == 409


def test_listar_clientes():
    """GET /clientes/ deve retornar lista."""
    client.post("/clientes/", json=CLIENTE_VALIDO)
    resp = client.get("/clientes/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_buscar_cliente_inexistente():
    """GET /clientes/9999 deve retornar 404."""
    resp = client.get("/clientes/9999")
    assert resp.status_code == 404


# ── CT-10: Campos obrigatórios ───────────────────────────────
def test_ct10_sem_razao_social():
    """CT-10: Razão social obrigatória."""
    resp = client.post("/clientes/", json={
        "cnpj": "11.222.333/0001-81",
        "email": "x@x.com",
    })
    assert resp.status_code == 422


def test_ct10_sem_cnpj():
    """CT-10: CNPJ obrigatório."""
    resp = client.post("/clientes/", json={
        "razao_social": "Empresa",
        "email": "x@x.com",
    })
    assert resp.status_code == 422
