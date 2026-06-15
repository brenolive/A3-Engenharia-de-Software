"""
Script: Popula empresas de manutenção no banco.
Executar da raiz: python populate_empresas.py
"""

import sys
sys.path.insert(0, ".")

from backend.database import SessionLocal, init_db
from backend.models.empresa_manutencao import EmpresaManutencao

init_db()

empresas = [
    EmpresaManutencao(
        cnpj          = "23.456.789/0001-10",
        razao_social  = "TecnoMaq Serviços Industriais LTDA",
        nome_fantasia = "TecnoMaq",
        email         = "contato@tecnomaq.com.br",
        telefone      = "(11) 3344-5566",
        especialidade = "Manutenção de serras e equipamentos de corte",
    ),
    EmpresaManutencao(
        cnpj          = "34.567.890/0001-22",
        razao_social  = "SerraFix Manutenção de Equipamentos LTDA",
        nome_fantasia = "SerraFix",
        email         = "suporte@serrafix.com.br",
        telefone      = "(11) 4455-6677",
        especialidade = "Manutenção de lixadeiras e acabamento industrial",
    ),
    EmpresaManutencao(
        cnpj          = "45.678.901/0001-33",
        razao_social  = "HidroPress Técnica Industrial LTDA",
        nome_fantasia = "HidroPress",
        email         = "atendimento@hidropress.com.br",
        telefone      = "(11) 5566-7788",
        especialidade = "Manutenção de prensas hidráulicas e equipamentos pesados",
    ),
]

db = SessionLocal()
try:
    for emp in empresas:
        existe = db.query(EmpresaManutencao).filter(
            EmpresaManutencao.cnpj == emp.cnpj
        ).first()
        if not existe:
            db.add(emp)
    db.commit()
    print("✅ Empresas de manutenção cadastradas com sucesso!")
    
    todas = db.query(EmpresaManutencao).all()
    for e in todas:
        print(f"  → [{e.id_empresa_manut}] {e.razao_social} ({e.cnpj})")
finally:
    db.close()
