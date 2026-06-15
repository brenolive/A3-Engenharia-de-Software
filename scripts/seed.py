"""
Popula o banco com dados de exemplo — Madeira Verde.
Execute na raiz do projeto: python scripts/seed.py

Flags:
    --limpar    apaga todos os dados antes de inserir (recomendado na 1ª vez)
    --verbose   exibe cada registro inserido

Modo padrão: ADICIONA por cima, ignora duplicatas silenciosamente.
"""

import sys
import os
import argparse
from datetime import date, timedelta

# ── FIX CRÍTICO: força CWD = raiz do projeto ─────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_SCRIPT_DIR)
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Seed — Madeira Verde")
parser.add_argument("--limpar",  action="store_true",
                    help="Apaga todos os dados antes de inserir")
parser.add_argument("--verbose", action="store_true",
                    help="Exibe cada registro inserido")
args = parser.parse_args()

print(f"[seed] CWD : {os.getcwd()}")
print(f"[seed] Banco: {os.path.join(os.getcwd(), 'backend', 'madeira_verde.db')}")

# ── Imports do projeto (APÓS o chdir) ─────────────────────────────────────────
from backend.database import SessionLocal, init_db
from backend.models.cliente            import Cliente
from backend.models.fornecedor         import Fornecedor, FornecedorComponente
from backend.models.componente         import (
    Componente, MateriaPrima, MaterialDiverso, Maquina, Ferramenta,
)
from backend.models.produto            import Produto, ProdutoComponente
from backend.models.empregado          import Empregado
from backend.models.encomenda          import Encomenda, ItemEncomenda
from backend.models.empresa_manutencao import EmpresaManutencao
from backend.models.manutencao         import Manutencao
from sqlalchemy                         import text

# ── Garante tabelas ───────────────────────────────────────────────────────────
init_db()

# ── Contadores ────────────────────────────────────────────────────────────────
_cnt: dict[str, int] = {}

def _log(entidade: str, nome: str = ""):
    _cnt[entidade] = _cnt.get(entidade, 0) + 1
    if args.verbose:
        print(f"  [+] {entidade:28s} {nome}")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def existe(model, **filtros) -> bool:
    return db.query(model).filter_by(**filtros).first() is not None

def get_or_none(model, **filtros):
    return db.query(model).filter_by(**filtros).first()

def hoje(delta: int = 0) -> date:
    return date.today() + timedelta(days=delta)


# ─────────────────────────────────────────────────────────────────────────────
# LIMPAR (ordem reversa de FK)
# ─────────────────────────────────────────────────────────────────────────────
def limpar_banco():
    print("\n⚠️  Limpando banco de dados...")
    tabelas = [
        "manutencao",
        "item_encomenda",
        "encomenda",
        "fornecedor_componente",
        "produto_componente",
        "ferramenta",
        "maquina",
        "material_diverso",
        "materia_prima",
        "componente",
        "produto",
        "fornecedor",
        "empresa_manutencao",
        "empregado",
        "cliente",
    ]
    for t in tabelas:
        try:
            db.execute(text(f"DELETE FROM {t}"))
            if args.verbose:
                print(f"  🗑  {t}")
        except Exception as e:
            print(f"  ⚠️  {t}: {e}")
    db.commit()
    print("✅ Banco limpo.\n")


# ─────────────────────────────────────────────────────────────────────────────
# 1. CLIENTES
# ─────────────────────────────────────────────────────────────────────────────
def seed_clientes():
    print("👤 Clientes...")
    dados = [
        dict(cnpj="11.222.333/0001-81", razao_social="Construtora Horizonte LTDA",
             nome_fantasia="Horizonte",
             email="compras@horizonte.com.br",    telefone="(11) 3000-1001",
             cidade="São Paulo",        estado="SP"),
        dict(cnpj="22.333.444/0001-70", razao_social="Móveis Bela Vista S.A.",
             nome_fantasia="Bela Vista Móveis",
             email="pedidos@belavista.com.br",    telefone="(11) 3000-2002",
             cidade="Campinas",         estado="SP"),
        dict(cnpj="33.444.555/0001-60", razao_social="Madeireira Pinus Forte LTDA",
             nome_fantasia="Pinus Forte",
             email="comercial@pinusforte.com.br", telefone="(41) 3100-3003",
             cidade="Curitiba",         estado="PR"),
        dict(cnpj="44.555.666/0001-49", razao_social="Decoração & Arte EIRELI",
             nome_fantasia="DecoArte",
             email="contato@decoarte.com.br",     telefone="(21) 2200-4004",
             cidade="Rio de Janeiro",   estado="RJ"),
        dict(cnpj="55.666.777/0001-38", razao_social="Hotel Serra Verde S.A.",
             nome_fantasia="Serra Verde",
             email="compras@serraverde.com.br",   telefone="(31) 3300-5005",
             cidade="Belo Horizonte",   estado="MG"),
        dict(cnpj="66.777.888/0001-27", razao_social="Escritórios Modernos LTDA",
             nome_fantasia="EscrMod",
             email="suprimentos@escrmod.com.br",  telefone="(51) 3400-6006",
             cidade="Porto Alegre",     estado="RS"),
        dict(cnpj="77.888.999/0001-16", razao_social="Pousada Madeira & Mel LTDA",
             nome_fantasia="Madeira & Mel",
             email="reservas@madeiraemel.com.br", telefone="(48) 3500-7007",
             cidade="Florianópolis",    estado="SC"),
    ]
    for d in dados:
        if not existe(Cliente, cnpj=d["cnpj"]):
            db.add(Cliente(**d))
            _log("Cliente", d["razao_social"])
    db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 2. FORNECEDORES
# ─────────────────────────────────────────────────────────────────────────────
def seed_fornecedores():
    print("🏭 Fornecedores...")
    dados = [
        dict(cnpj="88.999.000/0001-05",
             razao_social="Madeiras do Sul Distribuidora LTDA",
             nome_fantasia="MadSul",
             email="vendas@madsul.com.br",           telefone="(51) 3600-8008",
             cidade="Porto Alegre",   estado="RS"),
        dict(cnpj="99.000.111/0001-94",
             razao_social="Ferragens Gerais S.A.",
             nome_fantasia="FerraGeral",
             email="comercial@ferragerais.com.br",   telefone="(11) 3700-9009",
             cidade="São Paulo",      estado="SP"),
        dict(cnpj="10.111.222/0001-83",
             razao_social="Tintas & Vernizes Nordeste LTDA",
             nome_fantasia="TintaNord",
             email="pedidos@tintanord.com.br",       telefone="(81) 3800-1010",
             cidade="Recife",         estado="PE"),
        dict(cnpj="20.222.333/0001-72",
             razao_social="Equipamentos Industriais Centro-Oeste S.A.",
             nome_fantasia="EquipCO",
             email="vendas@equipco.com.br",          telefone="(62) 3900-2020",
             cidade="Goiânia",        estado="GO"),
        dict(cnpj="30.333.444/0001-61",
             razao_social="Colagem e Fixação Premium EIRELI",
             nome_fantasia="ColFix",
             email="atendimento@colfix.com.br",      telefone="(43) 3100-3030",
             cidade="Londrina",       estado="PR"),
    ]
    for d in dados:
        if not existe(Fornecedor, cnpj=d["cnpj"]):
            db.add(Fornecedor(**d))
            _log("Fornecedor", d["razao_social"])
    db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 3. COMPONENTES
# ─────────────────────────────────────────────────────────────────────────────
def _add_comp(nome: str, tipo: str, descricao: str | None = None) -> int:
    c = get_or_none(Componente, nome=nome, tipo_componente=tipo)
    if c:
        return c.id_componente
    c = Componente(nome=nome, tipo_componente=tipo, descricao=descricao)
    db.add(c)
    db.flush()
    _log("Componente", nome)
    return c.id_componente


def seed_componentes() -> dict[str, int]:
    print("🔩 Componentes...")
    ids: dict[str, int] = {}

    # Matérias-primas
    mp_data = [
        ("Madeira de Pinho",    "Tábuas de pinho serrado, secagem natural",
         "Brasil", "Pinho",    "FSC"),
        ("Madeira de Carvalho", "Carvalho europeu, alta durabilidade",
         "Europa", "Carvalho", "PEFC"),
        ("Madeira de Cedro",    "Cedro rosa nacional, resistente a cupins",
         "Brasil", "Cedro",    "FSC"),
        ("Madeira MDF 18mm",    "MDF resinado 18mm, uso interno",
         "Brasil", "MDF",      "FSC"),
        ("Espuma D-28",         "Espuma de alta densidade para estofados",
         "Brasil", "Espuma",   None),
        ("Couro Natural",       "Couro bovino curtido, acabamento natural",
         "Brasil", "Couro",    None),
    ]
    for nome, desc, origem, tipo_mad, cert in mp_data:
        id_c = _add_comp(nome, "MATERIA_PRIMA", desc)
        ids[nome] = id_c
        if not existe(MateriaPrima, id_componente=id_c):
            db.add(MateriaPrima(id_componente=id_c,
                                origem=origem,
                                tipo_madeira=tipo_mad,
                                certificacao=cert))

    # Materiais diversos
    md_data = [
        ("Parafuso M8 Inox",     "Parafuso sextavado M8×40mm inox",
         "Fixação",    "Inox Premium"),
        ("Lixa Grão 120",        "Lixa para madeira, grão 120",
         "Abrasivo",   "Norton"),
        ("Verniz Maritimo",      "Verniz de alta resistência para móveis",
         "Acabamento", "Sayerlack"),
        ("Cola PVA para Madeira","Cola branca PVA de alta resistência",
         "Adesivo",    "Cascorez"),
        ("Dobradiça 35mm",       "Dobradiça de caneco para porta MDF",
         "Fixação",    "Hafele"),
        ("Corrediça 400mm",      "Corrediça telescópica para gaveta",
         "Fixação",    "Grass"),
        ("Fita de Borda PVC",    "Fita de borda 22mm para MDF",
         "Acabamento", "Rehau"),
    ]
    for nome, desc, cat, marca in md_data:
        id_c = _add_comp(nome, "MATERIAL_DIVERSO", desc)
        ids[nome] = id_c
        if not existe(MaterialDiverso, id_componente=id_c):
            db.add(MaterialDiverso(id_componente=id_c,
                                   categoria=cat, marca=marca))

    # Máquinas
    maq_data = [
        ("Serra Circular Industrial",
         "Serra de bancada para corte de madeira",
         "SC-400",  "Makita",  "MK-SC-001", 120, date(2021, 3, 15), False),
        ("Plaina Desengrossadeira",
         "Plaina para nivelamento de superfícies",
         "PD-330",  "Invicta", "IV-PD-002",  96, date(2020, 7, 10), False),
        ("Tupia de Mesa",
         "Tupia para frisos e molduras",
         "TM-6200", "Bosch",   "BS-TM-003",  84, date(2022, 1, 20), True),
        ("Lixadeira de Cinta",
         "Lixadeira industrial para acabamento superficial",
         "LC-150",  "Makita",  "MK-LC-004",  96, date(2021, 9, 5),  False),
    ]
    for nome, desc, modelo, fab, serie, vida, compra, em_man in maq_data:
        id_c = _add_comp(nome, "MAQUINA", desc)
        ids[nome] = id_c
        if not existe(Maquina, id_componente=id_c):
            db.add(Maquina(id_componente=id_c,
                           modelo=modelo, fabricante=fab,
                           numero_serie=serie,
                           tempo_medio_vida=vida,
                           data_compra=compra,
                           em_manutencao=em_man))

    # Ferramentas
    ferr_data = [
        ("Trado Espiral 20mm",   "Trado para furação em madeira maciça",
         "Furação", "Tramontina", "TR-TAR-001"),
        ("Formão de Talhe 25mm", "Formão profissional para encaixes",
         "Talhe",   "Stanley",    "ST-FRM-002"),
        ("Grampeador Pneumático","Grampeador para estruturas estofadas",
         "Fixação", "Puma",       "PM-GRP-003"),
    ]
    for nome, desc, tipo_f, marca, serie in ferr_data:
        id_c = _add_comp(nome, "FERRAMENTA", desc)
        ids[nome] = id_c
        if not existe(Ferramenta, id_componente=id_c):
            db.add(Ferramenta(id_componente=id_c,
                              tipo_ferramenta=tipo_f,
                              marca=marca,
                              numero_serie=serie))

    db.flush()
    return ids


# ─────────────────────────────────────────────────────────────────────────────
# 4. PRODUTOS
# ─────────────────────────────────────────────────────────────────────────────
def seed_produtos() -> dict[str, int]:
    print("🪑 Produtos...")
    dados = [
        dict(codigo="MESA-001",
             nome="Mesa de Jantar 6 Lugares em Carvalho",
             categoria="Mesa",    preco_unitario=2800.00, ativo=True,
             descricao="Mesa retangular em carvalho maciço, 6 lugares, acabamento natural"),
        dict(codigo="MESA-002",
             nome="Mesa de Centro Rústica em Pinho",
             categoria="Mesa",    preco_unitario=980.00,  ativo=True,
             descricao="Mesa de centro retangular, estilo rústico, madeira de pinho"),
        dict(codigo="MESA-003",
             nome="Mesa Rústica em Madeira de Demolição",
             categoria="Mesa",    preco_unitario=3500.00, ativo=True,
             descricao="Mesa em madeira de demolição reaproveitada, peça única"),
        dict(codigo="CAD-001",
             nome="Cadeira de Jantar com Encosto em Cedro",
             categoria="Cadeira", preco_unitario=450.00,  ativo=True,
             descricao="Cadeira com encosto vazado, assento estofado, cedro nacional"),
        dict(codigo="ARM-001",
             nome="Armário Rústico 2 Portas em Pinho",
             categoria="Armário", preco_unitario=1850.00, ativo=True,
             descricao="Armário de 2 portas com dobradiças de ferro, pinho natural"),
        dict(codigo="ARM-002",
             nome="Armário Multiuso em Cedro 4 Gavetas",
             categoria="Armário", preco_unitario=2100.00, ativo=True,
             descricao="Armário multiuso com 4 gavetas deslizantes, cedro rosa"),
        dict(codigo="CAM-001",
             nome="Cama de Casal em Madeira de Cedro",
             categoria="Cama",    preco_unitario=2200.00, ativo=True,
             descricao="Cama de casal Queen size, cabeceira ripada, cedro nacional"),
        dict(codigo="EST-001",
             nome="Estante em Madeira Maciça 5 Prateleiras",
             categoria="Estante", preco_unitario=1350.00, ativo=True,
             descricao="Estante de parede com 5 prateleiras reguláveis, pinho tratado"),
        dict(codigo="BAN-001",
             nome="Banco Rústico em Pinus",
             categoria="Cadeira", preco_unitario=320.00,  ativo=True,
             descricao="Banco sem encosto em pinus tratado, ideal para áreas externas"),
        dict(codigo="SOF-001",
             nome="Sofá 3 Lugares em Estrutura de Carvalho",
             categoria="Sofá",    preco_unitario=4200.00, ativo=True,
             descricao="Sofá com estrutura em carvalho, almofadas removíveis"),
    ]

    ids: dict[str, int] = {}
    for d in dados:
        if not existe(Produto, codigo=d["codigo"]):
            p = Produto(**d)
            db.add(p)
            db.flush()
            _log("Produto", d["nome"])
        ids[d["codigo"]] = get_or_none(Produto, codigo=d["codigo"]).id_produto

    db.flush()
    return ids


# ─────────────────────────────────────────────────────────────────────────────
# 5. VÍNCULOS  Produto ↔ Componente
# ─────────────────────────────────────────────────────────────────────────────
def seed_produto_componentes(ids_prod: dict, ids_comp: dict):
    print("🔗 Produto ↔ Componente...")

    def _pc(codigo: str, nome_comp: str,
            qtd: float, unid: str, tempo: float | None = None):
        id_p = ids_prod.get(codigo)
        id_c = ids_comp.get(nome_comp)
        if not id_p or not id_c:
            if args.verbose:
                print(f"  ⚠️  skip {codigo} ← {nome_comp}")
            return
        if not existe(ProdutoComponente, id_produto=id_p, id_componente=id_c):
            db.add(ProdutoComponente(
                id_produto=id_p, id_componente=id_c,
                quantidade_necessaria=qtd,
                unidade_medida=unid,
                tempo_uso_horas=tempo,
            ))
            _log("ProdutoComp", f"{codigo} ← {nome_comp}")

    _pc("MESA-001", "Madeira de Carvalho",       8.0, "m²")
    _pc("MESA-001", "Parafuso M8 Inox",         24.0, "un")
    _pc("MESA-001", "Verniz Maritimo",            2.0, "litro")
    _pc("MESA-001", "Serra Circular Industrial",  1.0, "un",   4.0)

    _pc("MESA-002", "Madeira de Pinho",           4.0, "m²")
    _pc("MESA-002", "Lixa Grão 120",              3.0, "un")
    _pc("MESA-002", "Cola PVA para Madeira",      0.5, "litro")

    _pc("MESA-003", "Madeira de Pinho",          10.0, "m²")
    _pc("MESA-003", "Verniz Maritimo",             3.0, "litro")
    _pc("MESA-003", "Lixa Grão 120",               5.0, "un")

    _pc("CAD-001",  "Madeira de Cedro",            1.5, "m²")
    _pc("CAD-001",  "Espuma D-28",                 0.5, "m²")
    _pc("CAD-001",  "Couro Natural",               0.8, "m²")
    _pc("CAD-001",  "Formão de Talhe 25mm",        1.0, "un",  2.0)

    _pc("ARM-001",  "Madeira de Pinho",            6.0, "m²")
    _pc("ARM-001",  "Cola PVA para Madeira",       1.0, "litro")
    _pc("ARM-001",  "Dobradiça 35mm",              4.0, "un")
    _pc("ARM-001",  "Parafuso M8 Inox",           20.0, "un")

    _pc("ARM-002",  "Madeira de Cedro",            5.0, "m²")
    _pc("ARM-002",  "Corrediça 400mm",             8.0, "un")
    _pc("ARM-002",  "Fita de Borda PVC",          10.0, "metro")
    _pc("ARM-002",  "Parafuso M8 Inox",           16.0, "un")

    _pc("CAM-001",  "Madeira de Cedro",            5.0, "m²")
    _pc("CAM-001",  "Espuma D-28",                 2.0, "m²")
    _pc("CAM-001",  "Couro Natural",               1.5, "m²")
    _pc("CAM-001",  "Serra Circular Industrial",   1.0, "un",  3.0)

    _pc("EST-001",  "Madeira de Pinho",            3.5, "m²")
    _pc("EST-001",  "Madeira MDF 18mm",            1.0, "m²")
    _pc("EST-001",  "Fita de Borda PVC",           8.0, "metro")
    _pc("EST-001",  "Parafuso M8 Inox",           12.0, "un")

    _pc("BAN-001",  "Madeira de Pinho",            1.5, "m²")
    _pc("BAN-001",  "Parafuso M8 Inox",            8.0, "un")
    _pc("BAN-001",  "Lixa Grão 120",               1.0, "un")

    _pc("SOF-001",  "Madeira de Carvalho",         4.0, "m²")
    _pc("SOF-001",  "Espuma D-28",                 4.0, "m²")
    _pc("SOF-001",  "Couro Natural",               6.0, "m²")
    _pc("SOF-001",  "Grampeador Pneumático",       1.0, "un",  3.0)

    db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 6. VÍNCULOS  Fornecedor ↔ Componente
# ─────────────────────────────────────────────────────────────────────────────
def seed_fornecedor_componente(ids_comp: dict):
    print("🔗 Fornecedor ↔ Componente...")

    forn = {f.cnpj: f.id_fornecedor
            for f in db.query(Fornecedor).all()}

    madsul    = forn.get("88.999.000/0001-05")
    ferrager  = forn.get("99.000.111/0001-94")
    tintanord = forn.get("10.111.222/0001-83")
    equipco   = forn.get("20.222.333/0001-72")
    colfix    = forn.get("30.333.444/0001-61")

    vinculos = [
        (madsul,    "Madeira de Pinho",            120.00,  5, True),
        (madsul,    "Madeira de Carvalho",          280.00,  7, True),
        (madsul,    "Madeira de Cedro",             200.00,  6, False),
        (madsul,    "Madeira MDF 18mm",              52.00,  4, True),
        (ferrager,  "Parafuso M8 Inox",               0.45,  3, True),
        (ferrager,  "Dobradiça 35mm",                 3.20,  5, True),
        (ferrager,  "Corrediça 400mm",               28.00,  7, True),
        (ferrager,  "Trado Espiral 20mm",            180.00, 10, False),
        (ferrager,  "Formão de Talhe 25mm",          120.00,  8, True),
        (tintanord, "Verniz Maritimo",                85.00,  4, True),
        (tintanord, "Fita de Borda PVC",               1.80,  3, True),
        (tintanord, "Lixa Grão 120",                   2.50,  3, True),
        (colfix,    "Cola PVA para Madeira",           22.00,  3, True),
        (equipco,   "Serra Circular Industrial",        0.00, 30, False),
        (equipco,   "Tupia de Mesa",                    0.00, 30, False),
        (equipco,   "Lixadeira de Cinta",               0.00, 30, False),
    ]

    for id_f, nome_c, preco, prazo, pref in vinculos:
        id_c = ids_comp.get(nome_c)
        if not id_f or not id_c:
            continue
        if not existe(FornecedorComponente,
                      id_fornecedor=id_f, id_componente=id_c):
            db.add(FornecedorComponente(
                id_fornecedor=id_f,
                id_componente=id_c,
                preco_unitario=preco,
                prazo_entrega_dias=prazo,
                fornecedor_preferencial=pref,
            ))
            _log("FornecedorComp", f"{id_f} → {nome_c}")

    db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 7. EMPREGADOS
# ─────────────────────────────────────────────────────────────────────────────
def seed_empregados() -> dict[str, int]:
    print("👷 Empregados...")

    dados = [
        dict(matricula="MAT-010", nome="Ricardo Almeida Neves",
             cpf="111.222.333-01", cargo="Diretor de Operações",
             salario=15000.00, data_admissao=date(2018, 1, 10),
             email="ricardo@madeiraverde.com.br",
             qualificacoes="MBA Gestão Industrial, 15 anos de experiência",
             id_supervisor=None),
        dict(matricula="MAT-011", nome="Simone Barbosa Reis",
             cpf="111.222.333-02", cargo="Gerente de Produção",
             salario=9500.00, data_admissao=date(2019, 3, 5),
             email="simone@madeiraverde.com.br",
             qualificacoes="Eng. Mecânica, especialização em Lean Manufacturing",
             id_supervisor=None),
        dict(matricula="MAT-012", nome="Eduardo Campos Lima",
             cpf="111.222.333-03", cargo="Gerente Comercial",
             salario=9000.00, data_admissao=date(2019, 6, 12),
             email="eduardo@madeiraverde.com.br",
             qualificacoes="Adm. de Empresas, pós em Vendas B2B",
             id_supervisor=None),
        dict(matricula="MAT-013", nome="Fernanda Rocha Teixeira",
             cpf="111.222.333-04", cargo="Encarregada de Marcenaria",
             salario=5800.00, data_admissao=date(2020, 2, 18),
             email="fernanda@madeiraverde.com.br",
             qualificacoes="Técnica em Marcenaria, SENAI",
             id_supervisor=None),
        dict(matricula="MAT-014", nome="Bruno Souza Martins",
             cpf="111.222.333-05", cargo="Encarregado de Acabamento",
             salario=5200.00, data_admissao=date(2020, 8, 1),
             email="bruno@madeiraverde.com.br",
             qualificacoes="Técnico em Pintura e Acabamento",
             id_supervisor=None),
        dict(matricula="MAT-015", nome="Diego Moreira Costa",
             cpf="111.222.333-06", cargo="Marceneiro",
             salario=3200.00, data_admissao=date(2021, 4, 10),
             email="diego@madeiraverde.com.br",
             qualificacoes="Curso Marcenaria Básica e Avançada",
             id_supervisor=None),
        dict(matricula="MAT-016", nome="Larissa Pinto Ferreira",
             cpf="111.222.333-07", cargo="Auxiliar de Produção",
             salario=2400.00, data_admissao=date(2022, 9, 5),
             email="larissa@madeiraverde.com.br",
             qualificacoes="Ensino Médio Completo, curso NR-12",
             id_supervisor=None),
        dict(matricula="MAT-017", nome="Paulo Henrique Dias",
             cpf="111.222.333-08", cargo="Operador de Máquinas",
             salario=3600.00, data_admissao=date(2021, 11, 22),
             email="paulo@madeiraverde.com.br",
             qualificacoes="Técnico em Eletromecânica, NR-12 e NR-13",
             id_supervisor=None),
        dict(matricula="MAT-018", nome="Juliana Ferraz Oliveira",
             cpf="111.222.333-09", cargo="Desenhista Técnica",
             salario=4100.00, data_admissao=date(2021, 5, 3),
             email="juliana@madeiraverde.com.br",
             qualificacoes="Tecnólogo em Design de Móveis, AutoCAD",
             id_supervisor=None),
    ]

    ids: dict[str, int] = {}
    for d in dados:
        if not existe(Empregado, matricula=d["matricula"]):
            e = Empregado(**d)
            db.add(e)
            db.flush()
            _log("Empregado", d["nome"])
        ids[d["matricula"]] = get_or_none(
            Empregado, matricula=d["matricula"]).id_empregado

    # Hierarquia de supervisão
    hierarquia = {
        "MAT-011": "MAT-010",
        "MAT-012": "MAT-010",
        "MAT-013": "MAT-011",
        "MAT-014": "MAT-011",
        "MAT-015": "MAT-013",
        "MAT-016": "MAT-014",
        "MAT-017": "MAT-013",
        "MAT-018": "MAT-012",
    }
    for mat_sub, mat_sup in hierarquia.items():
        emp = get_or_none(Empregado, matricula=mat_sub)
        if emp and emp.id_supervisor is None:
            emp.id_supervisor = ids.get(mat_sup)

    db.flush()
    return ids


# ─────────────────────────────────────────────────────────────────────────────
# 8. EMPRESAS DE MANUTENÇÃO
# ─────────────────────────────────────────────────────────────────────────────
def seed_empresas_manutencao() -> dict[str, int]:
    print("🔧 Empresas de Manutenção...")
    dados = [
        dict(cnpj="40.444.555/0001-50",
             razao_social="TecnoServ Manutenção Industrial LTDA",
             nome_fantasia="TecnoServ",
             email="os@tecnoserv.com.br",
             telefone="(11) 3700-0001",
             especialidade="Manutenção de máquinas CNC e serras"),
        dict(cnpj="50.555.666/0001-40",
             razao_social="ElétricaMáx Serviços EIRELI",
             nome_fantasia="ElétricaMáx",
             email="eletrica@max.com.br",
             telefone="(11) 3800-0002",
             especialidade="Manutenção elétrica industrial"),
        dict(cnpj="60.666.777/0001-30",
             razao_social="PneumoFix Sistemas LTDA",
             nome_fantasia="PneumoFix",
             email="contato@pneumofix.com.br",
             telefone="(41) 3900-0003",
             especialidade="Sistemas pneumáticos e hidráulicos"),
    ]
    ids: dict[str, int] = {}
    for d in dados:
        if not existe(EmpresaManutencao, cnpj=d["cnpj"]):
            obj = EmpresaManutencao(**d)
            db.add(obj)
            db.flush()
            _log("EmpresaManut", d["razao_social"])
        ids[d["cnpj"]] = get_or_none(
            EmpresaManutencao, cnpj=d["cnpj"]).id_empresa_manut
    db.flush()
    return ids


# ─────────────────────────────────────────────────────────────────────────────
# 9. MANUTENÇÕES
# ─────────────────────────────────────────────────────────────────────────────
def seed_manutencoes(ids_comp: dict, ids_emp: dict, ids_empresa: dict):
    print("🛠️  Manutenções...")

    def _get_maq_id(nome_comp: str) -> int | None:
        id_c = ids_comp.get(nome_comp)
        if not id_c:
            return None
        maq = get_or_none(Maquina, id_componente=id_c)
        return maq.id_componente if maq else None

    tecnoserv   = ids_empresa.get("40.444.555/0001-50")
    eletricamax = ids_empresa.get("50.555.666/0001-40")
    pneumofix   = ids_empresa.get("60.666.777/0001-30")

    registros = [
        ("Serra Circular Industrial", "PREVENTIVA",
         "Revisão geral, troca de lâmina e lubrificação dos rolamentos",
         -40, -38, 1200.00, tecnoserv, "Paulo Henrique Dias"),
        ("Tupia de Mesa", "CORRETIVA",
         "Troca de rolamento do eixo principal — parada não programada",
         -25, -20, 3400.00, tecnoserv, "Paulo Henrique Dias"),
        ("Plaina Desengrossadeira", "PREVENTIVA",
         "Calibração de mesa e troca de facas de corte",
         -15, -13,  850.00, eletricamax, "Paulo Henrique Dias"),
        ("Lixadeira de Cinta", "PREVENTIVA",
         "Troca de cinta abrasiva e verificação de tensionamento",
         -10,  -9,  420.00, pneumofix, "Paulo Henrique Dias"),
        ("Serra Circular Industrial", "CORRETIVA",
         "Substituição de proteção do disco após falha de segurança",
          -5,  -4,  680.00, tecnoserv, "Paulo Henrique Dias"),
    ]

    for nome_maq, tipo, desc, di, df, custo, id_emp_man, responsavel in registros:
        id_maq = _get_maq_id(nome_maq)
        if not id_maq or not id_emp_man:
            continue
        if not existe(Manutencao, id_componente=id_maq,
                      tipo_manutencao=tipo, data_inicio=hoje(di)):
            db.add(Manutencao(
                id_componente       =id_maq,
                id_empresa_manut    =id_emp_man,
                tipo_manutencao     =tipo,
                descricao           =desc,
                data_inicio         =hoje(di),
                data_fim            =hoje(df),
                custo               =custo,
                responsavel_interno =responsavel,
            ))
            _log("Manutencao", f"{tipo} → {nome_maq}")

    db.flush()



# ─────────────────────────────────────────────────────────────────────────────
# 10. ENCOMENDAS
# ─────────────────────────────────────────────────────────────────────────────
def seed_encomendas(ids_prod: dict):
    print("📦 Encomendas...")

    cli = {c.razao_social: c.id_cliente
           for c in db.query(Cliente).all()}

    ultimo = db.query(Encomenda).order_by(
        Encomenda.id_encomenda.desc()).first()
    seq = [ultimo.id_encomenda if ultimo else 0]

    def _enc(cliente_rs: str, status: str, data_enc: date,
             itens_raw: list,
             desconto: float = 0.0,
             data_prev: date | None = None,
             data_real: date | None = None,
             obs: str | None = None):

        seq[0] += 1
        numero = f"ENC-{data_enc.strftime('%Y%m%d')}-{seq[0]:06d}"

        if existe(Encomenda, numero_encomenda=numero):
            return

        id_cli = cli.get(cliente_rs)
        if not id_cli:
            if args.verbose:
                print(f"  ⚠️  cliente não encontrado: {cliente_rs}")
            return

        valor_bruto = sum(q * p for _, q, p in itens_raw)
        valor_liq   = round(valor_bruto * (1 - desconto / 100), 2)

        enc = Encomenda(
            numero_encomenda      =numero,
            id_cliente            =id_cli,
            data_encomenda        =data_enc,
            data_entrega_prevista =data_prev,
            data_entrega_real     =data_real,
            status                =status,
            desconto_percentual   =desconto,
            valor_bruto           =valor_bruto,
            valor_liquido         =valor_liq,
            observacoes           =obs,
        )
        db.add(enc)
        db.flush()

        for cod, qtd, preco in itens_raw:
            id_p = ids_prod.get(cod)
            if id_p:
                db.add(ItemEncomenda(
                    id_encomenda   =enc.id_encomenda,
                    id_produto     =id_p,
                    quantidade     =qtd,
                    preco_unitario =preco,
                    subtotal       =round(qtd * preco, 2),
                ))

        _log("Encomenda", f"{numero} [{status}]")

    # 3 PENDENTES
    _enc("Decoração & Arte EIRELI", "PENDENTE",
         hoje(-2), [("CAD-001", 8, 450.00), ("MESA-002", 1, 980.00)],
         desconto=5.0, data_prev=hoje(20))

    _enc("Hotel Serra Verde S.A.", "PENDENTE",
         hoje(-1), [("CAM-001", 5, 2200.00), ("ARM-001", 2, 1850.00)],
         desconto=8.0, data_prev=hoje(30))

    _enc("Escritórios Modernos LTDA", "PENDENTE",
         hoje(), [("EST-001", 6, 1350.00), ("CAD-001", 12, 450.00)],
         desconto=10.0, data_prev=hoje(25))

    # 3 EM PRODUÇÃO
    _enc("Móveis Bela Vista S.A.", "EM_PRODUCAO",
         hoje(-10), [("MESA-001", 2, 2800.00), ("CAD-001", 8, 450.00)],
         desconto=5.0, data_prev=hoje(10),
         obs="Urgente — evento de lançamento")

    _enc("Pousada Madeira & Mel LTDA", "EM_PRODUCAO",
         hoje(-7), [("CAM-001", 8, 2200.00), ("MESA-002", 4, 980.00)],
         desconto=7.0, data_prev=hoje(15),
         obs="Reforma completa da pousada")

    _enc("Madeireira Pinus Forte LTDA", "EM_PRODUCAO",
         hoje(-5), [("ARM-002", 3, 2100.00), ("EST-001", 2, 1350.00)],
         desconto=5.0, data_prev=hoje(18),
         obs="Segunda fase do pedido anual")

    # 4 ENTREGUES
    _enc("Construtora Horizonte LTDA", "ENTREGUE",
         hoje(-45), [("MESA-001", 3, 2800.00), ("CAD-001", 12, 450.00)],
         desconto=10.0, data_prev=hoje(-20), data_real=hoje(-22),
         obs="Entregue antes do prazo")

    _enc("Madeireira Pinus Forte LTDA", "ENTREGUE",
         hoje(-60), [("ARM-001", 4, 1850.00), ("EST-001", 3, 1350.00)],
         desconto=5.0, data_prev=hoje(-35), data_real=hoje(-33),
         obs="Leve atraso por ajuste de acabamento")

    _enc("Decoração & Arte EIRELI", "ENTREGUE",
         hoje(-30), [("BAN-001", 10, 320.00), ("MESA-002", 2, 980.00)],
         desconto=0.0, data_prev=hoje(-15), data_real=hoje(-16),
         obs="Entrega antecipada aprovada pelo cliente")

    _enc("Hotel Serra Verde S.A.", "ENTREGUE",
         hoje(-50), [("SOF-001", 2, 4200.00), ("CAD-001", 6, 450.00)],
         desconto=12.0, data_prev=hoje(-25), data_real=hoje(-26),
         obs="Mobiliário para área de convivência")

    # 2 CANCELADAS
    _enc("Escritórios Modernos LTDA", "CANCELADA",
         hoje(-20), [("SOF-001", 3, 4200.00)],
         desconto=15.0, data_prev=hoje(-5),
         obs="Cancelada por mudança no projeto do cliente")

    _enc("Construtora Horizonte LTDA", "CANCELADA",
         hoje(-35), [("MESA-003", 1, 3500.00)],
         desconto=0.0, data_prev=hoje(-10),
         obs="Cancelada por restrição orçamentária")

    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    db = SessionLocal()
    try:
        if args.limpar:
            limpar_banco()

        seed_clientes()
        seed_fornecedores()
        ids_comp = seed_componentes()
        ids_prod = seed_produtos()
        seed_produto_componentes(ids_prod, ids_comp)
        seed_fornecedor_componente(ids_comp)
        ids_emp  = seed_empregados()
        ids_empr = seed_empresas_manutencao()
        seed_manutencoes(ids_comp, ids_emp, ids_empr)
        seed_encomendas(ids_prod)

        print("\n" + "=" * 55)
        print("  ✅ SEED CONCLUÍDO — Madeira Verde")
        print("=" * 55)
        for entidade, qtd in sorted(_cnt.items()):
            print(f"  {entidade:30s} → {qtd:3d} inseridos")
        print("=" * 55)
        print("\n📊 Dashboard terá:")
        print("  → 7 clientes  |  5 fornecedores  |  9 empregados")
        print("  → 10 produtos  |  20 componentes")
        print("  → Encomendas: 3 PENDENTE · 3 EM_PRODUCAO · 4 ENTREGUE · 2 CANCELADA")
        print("  → Pontualidade: 3 no prazo · 1 atrasada")
        print("  → Manutenções: 3 PREVENTIVA · 2 CORRETIVA")
        print("  → Hierarquia: 4 níveis")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro no seed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()
