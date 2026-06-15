"""
Testes: Manutenções
CT-03 — Registro de manutenção
CT-09 — Garantia vencida
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

TEST_URL = "sqlite:///./test_manut.db"
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


def criar_maquina() -> int:
    resp = client.post("/componentes/", json={
        "nome":            "Serra Circular Industrial",
        "tipo_componente": "MAQUINA",
        "modelo":          "Serra-X500",
        "data_compra":     "2022-01-15",
        "data_fim_garantia": "2024-01-15",  # Garantia vencida
    })
    return resp.json()["id_componente"]


def criar_empresa() -> int:
    resp = client.post("/manutencoes/empresas", json={
        "cnpj":          "99.888.777/0001-66",
        "razao_social":  "TechFix Manutenção LTDA",
        "especialidade": "Máquinas de corte",
    })
    return resp.json()["id_empresa_manut"]


# ── CT-03 ────────────────────────────────────────────────────
def test_ct03_registrar_manutencao():
    """CT-03: Registro de troca de peças com vínculo à empresa."""
    id_maq = criar_maquina()
    id_emp = criar_empresa()

    resp = client.post("/manutencoes/", json={
        "id_componente":    id_maq,
        "id_empresa_manut": id_emp,
        "tipo_manutencao":  "TROCA_PECAS",
        "data_inicio":      "2026-06-05",
        "custo":            1200.0,
        "pecas_substituidas": "Disco de corte, rolamento do eixo",
    })

    assert resp.status_code == 201
    data = resp.json()
    assert data["tipo_manutencao"]    == "TROCA_PECAS"
    assert data["id_empresa_manut"]   == id_emp
    assert float(data["custo"])       == 1200.0


def test_historico_manutencao():
    """Histórico deve retornar manutenções da máquina."""
    id_maq = criar_maquina()
    id_emp = criar_empresa()

    client.post("/manutencoes/", json={
        "id_componente":    id_maq,
        "id_empresa_manut": id_emp,
        "tipo_manutencao":  "PREVENTIVA",
        "data_inicio":      "2026-06-05",
    })

    resp = client.get(f"/manutencoes/maquina/{id_maq}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ── CT-09: Garantia vencida ───────────────────────────────────
def test_ct09_garantia_vencida():
    """
    CT-09: Sistema registra manutenção mesmo com garantia vencida.
    A verificação de garantia é informativa (via view SQL).
    """
    id_maq = criar_maquina()   # data_fim_garantia = 2024-01-15 (vencida)
    id_emp = criar_empresa()

    resp = client.post("/manutencoes/", json={
        "id_componente":    id_maq,
        "id_empresa_manut": id_emp,
        "tipo_manutencao":  "CORRETIVA",
        "data_inicio":      "2026-06-05",
        "descricao":        "Garantia vencida — manutenção corretiva paga",
    })
    # Sistema permite (não bloqueia), custo será cobrado da empresa
    assert resp.status_code == 201


def test_manutencao_em_ferramenta_bloqueada():
    """RN-08: Ferramenta não pode ter manutenção registrada."""
    ferramenta = client.post("/componentes/", json={
        "nome":            "Martelo de Borracha",
        "tipo_componente": "FERRAMENTA",
        "tipo_ferramenta": "Manual",
    })
    id_ferra = ferramenta.json()["id_componente"]
    id_emp   = criar_empresa()

    resp = client.post("/manutencoes/", json={
        "id_componente":    id_ferra,
        "id_empresa_manut": id_emp,
        "tipo_manutencao":  "PREVENTIVA",
        "data_inicio":      "2026-06-05",
    })
    assert resp.status_code == 422


def test_data_fim_antes_inicio():
    """RN-11: Data fim não pode ser anterior à data início."""
    id_maq = criar_maquina()
    id_emp = criar_empresa()

    resp = client.post("/manutencoes/", json={
        "id_componente":    id_maq,
        "id_empresa_manut": id_emp,
        "tipo_manutencao":  "CORRETIVA",
        "data_inicio":      "2026-06-05",
        "data_fim":         "2026-06-01",  # Anterior!
    })
    assert resp.status_code == 422
