"""
Adiciona os empregados MAT-001 a MAT-006 (dados originais do sistema)
sem apagar nenhum dado existente.
Execute: python scripts/seed_empregados_antigos.py
"""

import sys
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from datetime import date
from backend.database import SessionLocal
from backend.models.empregado import Empregado

db = SessionLocal()

def get_or_none(model, **filtros):
    return db.query(model).filter_by(**filtros).first()

try:
    dados = [
        dict(matricula="MAT-001", nome="Carlos Eduardo Mendes",
             cpf="111.111.111-01", email="carlos@madeiraverde.com.br",
             cargo="Gerente",              salario=8500.00,
             data_admissao=date(2020, 2, 1),
             qualificacoes="Gestão de Produção Industrial",
             id_supervisor=None),
        dict(matricula="MAT-002", nome="Fernanda Lima Costa",
             cpf="111.111.111-02", email="fernanda.lima@madeiraverde.com.br",
             cargo="Supervisor",           salario=5800.00,
             data_admissao=date(2021, 6, 15),
             qualificacoes="Técnica em Marcenaria, SENAI",
             id_supervisor=None),
        dict(matricula="MAT-003", nome="Roberto Alves Nunes",
             cpf="111.111.111-03", email="roberto@madeiraverde.com.br",
             cargo="Supervisor",           salario=5500.00,
             data_admissao=date(2021, 8, 1),
             qualificacoes="Técnico em Produção Industrial",
             id_supervisor=None),
        dict(matricula="MAT-004", nome="Juliana Souza Pires",
             cpf="111.111.111-04", email="juliana.souza@madeiraverde.com.br",
             cargo="Operador de Máquina",  salario=2800.00,
             data_admissao=date(2022, 2, 10),
             qualificacoes="NR-12, Operação de Máquinas",
             id_supervisor=None),
        dict(matricula="MAT-005", nome="Marcos Vinícius Dias",
             cpf="111.111.111-05", email="marcos@madeiraverde.com.br",
             cargo="Marceneiro",           salario=2650.00,
             data_admissao=date(2022, 5, 20),
             qualificacoes="Curso Marcenaria Básica",
             id_supervisor=None),
        dict(matricula="MAT-006", nome="Patrícia Andrade Silva",
             cpf="111.111.111-06", email="patricia@madeiraverde.com.br",
             cargo="Auxiliar de Produção", salario=2100.00,
             data_admissao=date(2023, 1, 9),
             qualificacoes="Ensino Médio Completo",
             id_supervisor=None),
    ]

    ids = {}
    for d in dados:
        if not get_or_none(Empregado, matricula=d["matricula"]):
            e = Empregado(**d)
            db.add(e)
            db.flush()
            print(f"  [+] {d['matricula']} — {d['nome']}")
        else:
            print(f"  [=] {d['matricula']} já existe, pulando")
        ids[d["matricula"]] = get_or_none(
            Empregado, matricula=d["matricula"]).id_empregado

    # Hierarquia
    hierarquia = {
        "MAT-002": "MAT-001",
        "MAT-003": "MAT-001",
        "MAT-004": "MAT-002",
        "MAT-005": "MAT-003",
        "MAT-006": "MAT-002",
    }
    for mat_sub, mat_sup in hierarquia.items():
        emp = get_or_none(Empregado, matricula=mat_sub)
        if emp and emp.id_supervisor is None:
            emp.id_supervisor = ids.get(mat_sup)

    db.commit()
    print(f"\n✅ Concluído! Total de empregados: {db.query(Empregado).count()}")

except Exception as e:
    db.rollback()
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
