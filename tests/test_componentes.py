"""
Testes: Componentes
CT-04 — Produto com componentes
CT-07 — Fornecedor N:N componentes
CT-08 — Auto-relacionamento de supervisão
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

TEST_URL = "sqlite:///./test_comp.db"
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


# ── CT-04: Produto com componentes ───────────────────────────
def test_ct04_produto_com_componentes():
    """CT-04: Produto deve aceitar múltiplos componentes vinculados."""
    # Cria componentes
    madeira = client.post("/componentes/", json={
        "nome": "MDF 15mm", "tipo_componente": "MATERIA_PRIMA",
        "tipo_madeira": "MDF",
    }).json()

    parafuso = client.post("/componentes/", json={
        "nome": "Parafuso 4mm", "tipo_componente": "MATERIAL_DIVERSO",
        "categoria": "Fixação",
    }).json()

    # Cria produto
    produto = client.post("/produtos/", json={
        "codigo": "EST-001", "nome": "Estante 6 Prateleiras",
        "preco_unitario": 450.0,
    }).json()

    id_prod = produto["id_produto"]

    # Vincula componentes
    r1 = client.post(f"/produtos/{id_prod}/componentes", json={
        "id_produto":            id_prod,
        "id_componente":         madeira["id_componente"],
        "quantidade_necessaria": 12.0,
        "unidade_medida":        "m2",
    })
    r2 = client.post(f"/produtos/{id_prod}/componentes", json={
        "id_produto":            id_prod,
        "id_componente":         parafuso["id_componente"],
        "quantidade_necessaria": 48.0,
        "unidade_medida":        "un",
    })

    assert r1.status_code == 201
    assert r2.status_code == 201

    # Consulta componentes do produto
    lista = client.get(f"/produtos/{id_prod}/componentes")
    assert lista.status_code == 200
    assert len(lista.json()) == 2


def test_componente_duplicado_no_produto():
    """CT-04b: Mesmo componente não pode ser vinculado duas vezes ao produto."""
    madeira = client.post("/componentes/", json={
        "nome": "Pinus", "tipo_componente": "MATERIA_PRIMA",
    }).json()

    produto = client.post("/produtos/", json={
        "codigo": "PROD-DUP", "nome": "Produto Dup", "preco_unitario": 100.0,
    }).json()

    dados = {
        "id_produto":            produto["id_produto"],
        "id_componente":         madeira["id_componente"],
        "quantidade_necessaria": 1.0,
        "unidade_medida":        "un",
    }
    client.post(f"/produtos/{produto['id_produto']}/componentes", json=dados)
    resp = client.post(f"/produtos/{produto['id_produto']}/componentes", json=dados)
    assert resp.status_code == 409


# ── CT-07: Fornecedor N:N componentes ───────────────────────
def test_ct07_fornecedor_multiplos_componentes():
    """CT-07: Fornecedor pode ser vinculado a múltiplos componentes."""
    fornecedor = client.post("/fornecedores/", json={
        "cnpj": "11.222.333/0001-81", "razao_social": "Madeirex LTDA",
    }).json()

    id_forn = fornecedor["id_fornecedor"]

    c1 = client.post("/componentes/", json={
        "nome": "Pinus Radiata", "tipo_componente": "MATERIA_PRIMA",
    }).json()
    c2 = client.post("/componentes/", json={
        "nome": "Cola PVA", "tipo_componente": "MATERIAL_DIVERSO",
    }).json()
    c3 = client.post("/componentes/", json={
        "nome": "Parafuso Torx", "tipo_componente": "MATERIAL_DIVERSO",
    }).json()

    for comp in [c1, c2, c3]:
        r = client.post(f"/fornecedores/{id_forn}/componentes", json={
            "id_fornecedor":  id_forn,
            "id_componente":  comp["id_componente"],
            "preco_unitario": 10.0,
        })
        assert r.status_code == 201

    lista = client.get(f"/fornecedores/{id_forn}/componentes")
    assert len(lista.json()) == 3


# ── CT-08: Auto-relacionamento de supervisão ─────────────────
def test_ct08_empregado_com_supervisor():
    """CT-08: Empregado pode ter supervisor definido."""
    supervisor = client.post("/empregados/", json={
        "matricula": "MAT-001", "nome": "João Silva", "cpf": "111.222.333-44",
        "cargo": "Gerente", "salario": 8000.0, "data_admissao": "2020-01-10",
    }).json()

    subordinado = client.post("/empregados/", json={
        "matricula":    "MAT-002",
        "nome":         "Maria Souza",
        "cpf":          "555.666.777-88",
        "cargo":        "Operadora",
        "salario":      3500.0,
        "data_admissao": "2022-03-15",
        "id_supervisor": supervisor["id_empregado"],
    })

    assert subordinado.status_code == 201
    data = subordinado.json()
    assert data["id_supervisor"] == supervisor["id_empregado"]


def test_ct08_supervisor_inexistente():
    """CT-08b: Supervisor com ID inexistente deve retornar 404."""
    resp = client.post("/empregados/", json={
        "matricula":    "MAT-003",
        "nome":         "Pedro Lima",
        "cpf":          "999.888.777-66",
        "cargo":        "Auxiliar",
        "salario":      2500.0,
        "data_admissao": "2023-06-01",
        "id_supervisor": 9999,  # Não existe
    })
    assert resp.status_code == 400
