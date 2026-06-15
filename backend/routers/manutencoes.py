"""Router: Manutenções de Máquinas + Empresas de Manutenção."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.componente import Componente, Maquina
from backend.models.manutencao import Manutencao
from backend.models.empresa_manutencao import EmpresaManutencao
from backend.schemas.manutencao import (
    EmpresaManutencaoCreate,
    EmpresaManutencaoResponse,
    ManutencaoCreate,
    ManutencaoResponse,
)
from backend.services.validacoes import validar_componente_e_maquina

router = APIRouter(prefix="/manutencoes", tags=["Manutenções"])


# ── Helper interno ───────────────────────────────────────────

def _enriquecer(manut: Manutencao, db: Session) -> ManutencaoResponse:
    """Popula componente_nome e empresa_nome no response."""
    comp = db.query(Componente).filter(
        Componente.id_componente == manut.id_componente
    ).first()
    empresa = db.query(EmpresaManutencao).filter(
        EmpresaManutencao.id_empresa_manut == manut.id_empresa_manut
    ).first()

    data = ManutencaoResponse.model_validate(manut)
    data.componente_nome = comp.nome if comp else None
    data.empresa_nome = (
        empresa.nome_fantasia or empresa.razao_social
    ) if empresa else None
    return data


# ── Empresas de Manutenção ───────────────────────────────────

@router.get("/empresas", response_model=List[EmpresaManutencaoResponse])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(EmpresaManutencao).all()


@router.post("/empresas", response_model=EmpresaManutencaoResponse, status_code=201)
def criar_empresa(dados: EmpresaManutencaoCreate, db: Session = Depends(get_db)):
    if db.query(EmpresaManutencao).filter(
        EmpresaManutencao.cnpj == dados.cnpj
    ).first():
        raise HTTPException(status_code=409, detail="CNPJ já cadastrado.")

    emp = EmpresaManutencao(**dados.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


# ── Manutenções ──────────────────────────────────────────────

@router.post("/", response_model=ManutencaoResponse, status_code=201)
def registrar_manutencao(dados: ManutencaoCreate, db: Session = Depends(get_db)):
    """
    RN-08: Somente MAQUINA pode ter manutenção.
    RN-09: Marca máquina como em_manutencao=True quando sem data_fim.
    """
    comp = db.query(Componente).filter(
        Componente.id_componente == dados.id_componente
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Componente não encontrado.")

    validar_componente_e_maquina(comp.tipo_componente)

    empresa = db.query(EmpresaManutencao).filter(
        EmpresaManutencao.id_empresa_manut == dados.id_empresa_manut
    ).first()
    if not empresa:
        raise HTTPException(
            status_code=404, detail="Empresa de manutenção não encontrada."
        )

    manut = Manutencao(**dados.model_dump())
    db.add(manut)

    # RN-09
    maquina = db.query(Maquina).filter(
        Maquina.id_componente == dados.id_componente
    ).first()
    if maquina:
        maquina.em_manutencao = dados.data_fim is None

    db.commit()
    db.refresh(manut)
    # ✅ Retorna com nomes populados
    return _enriquecer(manut, db)


@router.get("/", response_model=List[ManutencaoResponse])
def listar_manutencoes(db: Session = Depends(get_db)):
    return [_enriquecer(m, db) for m in db.query(Manutencao).all()]


@router.get("/maquina/{id_componente}", response_model=List[ManutencaoResponse])
def historico_maquina(id_componente: int, db: Session = Depends(get_db)):
    manutencoes = db.query(Manutencao).filter(
        Manutencao.id_componente == id_componente
    ).all()
    return [_enriquecer(m, db) for m in manutencoes]


@router.get("/{id_manutencao}", response_model=ManutencaoResponse)
def buscar_manutencao(id_manutencao: int, db: Session = Depends(get_db)):
    manut = db.query(Manutencao).filter(
        Manutencao.id_manutencao == id_manutencao
    ).first()
    if not manut:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada.")
    return _enriquecer(manut, db)


@router.delete("/{id_manutencao}", status_code=204)
def deletar_manutencao(id_manutencao: int, db: Session = Depends(get_db)):
    manut = db.query(Manutencao).filter(
        Manutencao.id_manutencao == id_manutencao
    ).first()
    if not manut:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada.")

    # RN-09: libera a máquina ao excluir manutenção em andamento
    if manut.data_fim is None:
        maquina = db.query(Maquina).filter(
            Maquina.id_componente == manut.id_componente
        ).first()
        if maquina:
            maquina.em_manutencao = False

    db.delete(manut)
    db.commit()
