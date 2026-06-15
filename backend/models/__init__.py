# Expõe todos os models para facilitar importação
from backend.models.cliente import Cliente
from backend.models.componente import (
    Componente,
    MateriaPrima,
    MaterialDiverso,
    Maquina,
    Ferramenta,
)
from backend.models.empregado import Empregado
from backend.models.empresa_manutencao import EmpresaManutencao
from backend.models.encomenda import Encomenda, ItemEncomenda
from backend.models.fornecedor import Fornecedor, FornecedorComponente
from backend.models.manutencao import Manutencao
from backend.models.produto import Produto, ProdutoComponente, ProdutoMaoObra

__all__ = [
    "Cliente",
    "Componente",
    "MateriaPrima",
    "MaterialDiverso",
    "Maquina",
    "Ferramenta",
    "Empregado",
    "EmpresaManutencao",
    "Encomenda",
    "ItemEncomenda",
    "Fornecedor",
    "FornecedorComponente",
    "Manutencao",
    "Produto",
    "ProdutoComponente",
    "ProdutoMaoObra",
]

