# 🌿 Sistema de Gestão Madeira Verde

> Trabalho Acadêmico — A3 2026/1 · Modelos, Métodos e Técnicas de Engenharia de Software  
> Universidade Anhembi Morumbi — Ciências da Computação

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.x-003B57?style=flat&logo=sqlite&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-23%20testes-brightgreen?style=flat&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/Licença-Acadêmica-lightgrey?style=flat)

---

## 📋 Sobre o Projeto

A **Fábrica de Móveis Madeira Verde** é uma empresa de manufatura que produz móveis sob encomenda, atendendo exclusivamente a **pessoas jurídicas** — varejistas de diversas regiões do Brasil.

Diante do crescimento da demanda e da complexidade operacional, foi desenvolvido um **sistema de informação integrado** para gerenciar os processos internos da empresa, incluindo:

- Cadastro de clientes PJ com validação de CNPJ
- Catálogo de produtos e componentes (com STI)
- Controle de fornecedores e empregados
- Registro e acompanhamento de encomendas
- Gestão de manutenção de máquinas
- Dashboard gerencial com KPIs

---

## 👥 Equipe

| Integrante | RA | Responsabilidade |
|---|---|---|
| **Breno Oliveira** | 12523143979 | Arquitetura, DevOps e Metodologias |
| **Cauã Máximo** | 12523138074 | Engenharia de Requisitos e Viabilidade |
| **Diego Maia** | 12523169668 | UML e Análise de Sistema |
| **Kauê Scatigno** | 12523164338 | Modelagem e Banco de Dados |

**Professor:** W. Fernando

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework Web | FastAPI |
| Servidor ASGI | Uvicorn — porta 8000 |
| ORM | SQLAlchemy |
| Banco de Dados | SQLite 3.x — `backend/madeira_verde.db` |
| Validação | Pydantic v2 |
| Frontend | HTML5 + CSS3 + JavaScript puro |
| Gráficos | Chart.js 4.4.0 via CDN |
| Testes | Pytest — 23 casos automatizados |
| Documentação | Swagger UI em `/docs` (automático) |
| Ambiente | Python venv · Windows 10/11 |

---

## 📁 Estrutura do Projeto

```
madeira_verde/
├── backend/
│   ├── main.py                     # Configuração FastAPI, CORS e routers
│   ├── database.py                 # Engine, SessionLocal, Base e PRAGMA FK
│   ├── models/                     # Modelos SQLAlchemy (ORM)
│   │   ├── cliente.py
│   │   ├── componente.py           # STI — discriminador tipo_componente
│   │   ├── empregado.py
│   │   ├── empresa_manutencao.py
│   │   ├── encomenda.py
│   │   ├── fornecedor.py
│   │   ├── manutencao.py
│   │   └── produto.py
│   ├── schemas/                    # Contratos Pydantic v2
│   │   ├── empregado.py
│   │   └── encomenda.py
│   ├── routers/                    # Endpoints REST
│   │   ├── clientes.py
│   │   ├── componentes.py
│   │   ├── dashboard.py
│   │   ├── empregados.py
│   │   ├── empresa_manutencao.py
│   │   ├── encomendas.py
│   │   ├── fornecedores.py
│   │   ├── manutencoes.py
│   │   └── produtos.py
│   └── services/                   # Lógica de negócio
│       ├── encomenda_service.py    # Factory Method — gerar_numero_encomenda()
│       └── validacoes.py           # Strategy — validar_cnpj()
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js                  # Centraliza todas as chamadas HTTP
│   │   ├── clientes.js
│   │   ├── componentes.js
│   │   ├── empregados.js
│   │   ├── encomendas.js
│   │   ├── fornecedores.js
│   │   ├── manutencoes.js
│   │   └── produtos.js
│   └── *.html                      # index, dashboard, clientes, produtos...
├── scripts/
│   ├── seed.py                     # Popula o banco com dados de teste
│   └── seed_empregados_antigos.py
└── tests/                          # 23 casos de teste Pytest
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.12+
- pip

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/madeira-verde.git
cd madeira-verde
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install fastapi uvicorn sqlalchemy pydantic pytest httpx
```

### 4. Suba o servidor

```bash
uvicorn backend.main:app --reload
```

O servidor estará disponível em: **http://localhost:8000**

### 5. (Opcional) Popule o banco com dados de exemplo

```bash
python scripts/seed.py --limpar --verbose
python scripts/seed_empregados_antigos.py
```

### 6. Acesse o sistema

| URL | Descrição |
|---|---|
| `http://localhost:8000` | Frontend — página inicial |
| `http://localhost:8000/docs` | Swagger UI — documentação interativa |
| `http://localhost:8000/redoc` | ReDoc — documentação alternativa |

---

## 🧪 Executando os Testes

```bash
pytest tests/ -v
```

**Resultado esperado:** 23 testes — ✅ 100% aprovados

| Caso de Teste | Requisitos Validados | Resultado |
|---|---|---|
| CT-01 | RF-02, RN-01 — Bloqueio de CPF e CNPJ inválido | ✅ Aprovado |
| CT-02 | RF-09, RF-11, RN-06 — Encomenda com desconto 10% | ✅ Aprovado |
| CT-03 | RF-12 — Manutenção vinculada à empresa especializada | ✅ Aprovado |
| CT-04 | RF-05, RN-04 — Produto com múltiplos componentes | ✅ Aprovado |
| CT-06 | RF-09, RN-04 — Encomenda com múltiplos produtos | ✅ Aprovado |
| CT-07 | RF-06, RN-05 — Fornecedor com múltiplos componentes | ✅ Aprovado |
| CT-08 | RF-07, RF-08, RN-10 — Hierarquia supervisor/subordinado | ✅ Aprovado |
| CT-09 | RF-12, RN-08 — Manutenção em máquina com garantia vencida | ✅ Aprovado |
| CT-10 | RF-01, RF-03 — Campos obrigatórios | ✅ Aprovado |
| CT-11 | RNF-07 — Integração entre as 3 camadas | ✅ Aprovado |

---

## 🏗️ Arquitetura

O sistema segue a **Arquitetura em Três Camadas (Three-Tier Architecture)**:

```
┌─────────────────────────────────────────────┐
│           CAMADA DE APRESENTAÇÃO            │
│      HTML5 · CSS3 · JavaScript puro         │
│   api.js centraliza todas as chamadas HTTP  │
└──────────────────┬──────────────────────────┘
                   │ HTTP / REST / JSON
┌──────────────────▼──────────────────────────┐
│            CAMADA DE NEGÓCIO                │
│     Python 3.12 · FastAPI · Pydantic v2     │
│         routers / services / schemas        │
└──────────────────┬──────────────────────────┘
                   │ SQLAlchemy ORM
┌──────────────────▼──────────────────────────┐
│             CAMADA DE DADOS                 │
│   SQLite · SQLAlchemy · PRAGMA FK = ON      │
│           madeira_verde.db                  │
└─────────────────────────────────────────────┘
```

---

## 🎯 Padrões de Projeto Implementados

| Padrão | Implementação | Localização |
|---|---|---|
| **Repository Pattern** | Acesso ao banco via SQLAlchemy ORM — sem SQL direto | `backend/models/` + `backend/routers/` |
| **Factory Method** | `gerar_numero_encomenda()` — gera ENC-AAAAMMDD-NNNNNN | `backend/services/encomenda_service.py` |
| **Strategy** | `validar_cnpj()` reutilizável entre módulos | `backend/services/validacoes.py` |
| **Dependency Injection** | `Depends(get_db)` em todos os endpoints | `backend/database.py` → todos os routers |
| **Facade** | Routers expõem interface REST simplificada | `backend/routers/*.py` |

---

## 🗄️ Banco de Dados — 10 Entidades (3FN)

| Entidade | Destaques |
|---|---|
| **CLIENTE** | `cnpj UNIQUE`, `email UNIQUE`, `data_cadastro NOT NULL` |
| **PRODUTO** | `codigo UNIQUE`, `preco_unitario`, `tempo_fabricacao` |
| **COMPONENTE** | STI — discriminador `tipo_componente`: MAQUINA / FERRAMENTA / MATERIA_PRIMA / MATERIAL_DIVERSO |
| **MAQUINA** | Extensão STI: `modelo`, `fabricante`, `numero_serie`, `em_manutencao BOOLEAN` |
| **EMPREGADO** | `matricula UNIQUE`, `id_supervisor FK` → auto-relacionamento |
| **FORNECEDOR** | `cnpj UNIQUE` |
| **ENCOMENDA** | `numero_encomenda UNIQUE`, `status` default PENDENTE, `valor_bruto`, `valor_liquido` |
| **ITEM_ENCOMENDA** | FK → ENCOMENDA (CASCADE DELETE), FK → PRODUTO, `subtotal` |
| **EMPRESA_MANUTENCAO** | `cnpj UNIQUE`, `especialidade` |
| **MANUTENCAO** | FK → COMPONENTE (tipo MAQUINA), `tipo_manutencao`: PREVENTIVA/CORRETIVA/TROCA_DE_PECAS |

**Relacionamentos N:N:**
- `PRODUTO ↔ COMPONENTE` → tabela `produto_componente`
- `FORNECEDOR ↔ COMPONENTE` → tabela `fornecedor_componente`

---

## 📜 Regras de Negócio

| Código | Regra |
|---|---|
| **RN-01** | Apenas CNPJ aceito — CPF bloqueado → HTTP 422 |
| **RN-02** | CNPJ e e-mail únicos no sistema |
| **RN-03** | Cliente só pode ser cadastrado como pessoa jurídica |
| **RN-04** | Componente pode estar em múltiplos produtos e vice-versa |
| **RN-05** | Fornecedor pode fornecer múltiplos componentes de categorias diferentes |
| **RN-06** | `valor_liquido = valor_bruto × (1 − desconto / 100)` |
| **RN-07** | Número encomenda: `ENC-AAAAMMDD-NNNNNN` |
| **RN-08** | Manutenção só para tipo MAQUINA → HTTP 422 |
| **RN-09** | Se `data_fim IS NULL` → `em_manutencao = True` |
| **RN-10** | Empregado não pode ser seu próprio supervisor → HTTP 400 |

---

## 📊 Requisitos Funcionais (16)

| Código | Requisito |
|---|---|
| RF-01 | Cadastro de clientes PJ com CNPJ, razão social, endereços e contatos |
| RF-02 | Validação de CNPJ — bloqueio de CPF e CNPJs inválidos |
| RF-03 | Cadastro de produtos com código, nome, cor, dimensões, peso, preço e tempo de fabricação |
| RF-04 | Cadastro de componentes nas 4 categorias (STI) |
| RF-05 | Associação componentes ↔ produtos com quantidade ou tempo de uso |
| RF-06 | Cadastro de fornecedores associados a componentes |
| RF-07 | Cadastro de empregados com matrícula, cargo, salário e hierarquia |
| RF-08 | Bloqueio de empregado como seu próprio supervisor |
| RF-09 | Encomendas com múltiplos produtos, data, desconto e valor líquido |
| RF-10 | Geração automática do número de encomenda no formato ENC-AAAAMMDD-NNNNNN |
| RF-11 | Cálculo automático do valor líquido com desconto percentual |
| RF-12 | Registro de manutenções vinculadas a empresas especializadas |
| RF-13 | Bloqueio de manutenção para componentes que não sejam Máquina |
| RF-14 | Dashboard com KPIs: totais, faturamento, status das encomendas |
| RF-15 | Exclusão de encomendas cadastradas incorretamente |
| RF-16 | Edição parcial de dados de clientes |

---

## 🔒 Requisitos Não Funcionais (9)

| Código | Requisito |
|---|---|
| RNF-01 | Acessível por navegador sem instalação adicional |
| RNF-02 | Tempo de resposta de consultas < 2 segundos |
| RNF-03 | Validação dos dados de entrada antes de persistir |
| RNF-04 | API REST com respostas em JSON |
| RNF-05 | Banco relacional normalizado até 3FN |
| RNF-06 | Integridade referencial via chaves estrangeiras |
| RNF-07 | Código organizado em camadas com responsabilidades bem definidas |
| RNF-08 | Executável em Windows com Python 3.12 |
| RNF-09 | Documentação interativa disponível em `/docs` (Swagger UI) |

---

## 🏃 Sprints do Projeto (Scrum)

| Sprint | Escopo | Entregável |
|---|---|---|
| Sprint 1 | Ambiente, banco de dados, modelo de Clientes, validação de CNPJ | Módulo de Clientes funcional com RN-01 e RN-02 |
| Sprint 2 | Produtos, Componentes (STI) e Fornecedores | Catálogo completo com associações produto-componente-fornecedor |
| Sprint 3 | Empregados com auto-relacionamento e Encomendas | Encomendas com cálculo automático de valor líquido |
| Sprint 4 | Manutenções, Empresas de Manutenção e Dashboard | Sistema de manutenção completo e painel com KPIs |
| Sprint 5 | Integração frontend-backend, testes e documentação | 23 testes passando, frontend integrado, documentação entregue |

---

## 📈 Dados do Banco (Seed)

| Entidade | Quantidade |
|---|---|
| Clientes | 7 |
| Fornecedores | 5 |
| Componentes | 20 |
| Produtos | 10 |
| Empregados | 15 (MAT-001 a MAT-018) |
| Encomendas | 12 (3 PENDENTE · 3 EM_PRODUCAO · 4 ENTREGUE · 2 CANCELADA) |
| Empresas de Manutenção | 3 |
| Manutenções | 5 (3 PREVENTIVA · 2 CORRETIVA) |

**KPIs do Dashboard:**
- 💰 Faturamento bruto: **R$ 130.110,00**
- 💵 Faturamento líquido: **R$ 119.764,10**
- 🎯 Ticket médio: **R$ 9.980,34**
- 🏆 Top cliente: **Hotel Serra Verde** — R$ 23.292,00
- 🏆 Top produto: **Cadeira de Jantar** — 46 unidades

---

## 🔧 Comandos Úteis

```bash
# Subir o servidor
uvicorn backend.main:app --reload

# Resetar e popular o banco
python scripts/seed.py --limpar --verbose

# Seed de empregados
python scripts/seed_empregados_antigos.py

# Executar todos os testes
pytest tests/ -v

# Executar testes com relatório de cobertura
pytest tests/ -v --tb=short
```

---

## 📄 Documentação

A documentação completa do projeto (29 páginas) está disponível no arquivo `A3 Engenharia de Software.pdf`, contendo:

1. Estudo de Viabilidade
2. Engenharia de Requisitos
3. Ciclo de Vida e Modelo de Processo
4. Padrões de Projeto
5. Arquitetura de Software e Infraestrutura
6. Diagrama Entidade-Relacionamento (DER)
7. Análise e Projeto (UML)
8. Diagramas de Sequência
9. Diagrama de Instalação e Pacotes
10. Integração Contínua e DevOps
11. Plano de Testes
12. Abordagem Ágil
13. Manual do Usuário
14. Manual do Administrador

---

## 📌 Observações

> Este projeto foi desenvolvido exclusivamente para fins acadêmicos como parte da disciplina **Modelos, Métodos e Técnicas de Engenharia de Software** — A3 2026/1.

---

*Universidade Anhembi Morumbi · Ciências da Computação · São Paulo · 2026*
