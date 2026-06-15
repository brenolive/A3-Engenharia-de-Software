"""Router: Empregados."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.empregado import Empregado
from backend.schemas.empregado import (
    EmpregadoCreate,
    EmpregadoResponse,
    EmpregadoUpdate,
)

router = APIRouter(prefix="/empregados", tags=["Empregados"])


# ============================================================
# HELPER — converte ORM → Response com supervisor_nome
# ============================================================
def _serializar(emp: Empregado, db: Session) -> EmpregadoResponse:
    supervisor_nome = None
    if emp.id_supervisor is not None:
        sup = db.get(Empregado, emp.id_supervisor)
        supervisor_nome = sup.nome if sup else None

    return EmpregadoResponse(
        id_empregado    = emp.id_empregado,
        matricula       = emp.matricula,
        nome            = emp.nome,
        cpf             = emp.cpf,
        email           = emp.email,
        telefone        = emp.telefone,
        cargo           = emp.cargo,
        salario         = float(emp.salario),
        data_admissao   = emp.data_admissao,
        qualificacoes   = emp.qualificacoes,
        id_supervisor   = emp.id_supervisor,
        supervisor_nome = supervisor_nome,
    )


# ============================================================
# POST — Criar empregado
# ============================================================
@router.post("/", response_model=EmpregadoResponse, status_code=201)
def criar_empregado(dados: EmpregadoCreate, db: Session = Depends(get_db)):

    if dados.id_supervisor is not None:
        sup = db.get(Empregado, dados.id_supervisor)
        if not sup:
            raise HTTPException(status_code=400,
                                detail="Supervisor não encontrado.")

    if db.query(Empregado).filter(
            Empregado.matricula == dados.matricula).first():
        raise HTTPException(status_code=409, detail="Matrícula já cadastrada.")

    if db.query(Empregado).filter(
            Empregado.cpf == dados.cpf).first():
        raise HTTPException(status_code=409, detail="CPF já cadastrado.")

    emp = Empregado(**dados.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return _serializar(emp, db)


# ============================================================
# GET — Listar todos (ordenado por matrícula)
# ============================================================
@router.get("/", response_model=List[EmpregadoResponse])
def listar_empregados(db: Session = Depends(get_db)):
    empregados = db.query(Empregado).order_by(Empregado.matricula).all()
    return [_serializar(e, db) for e in empregados]


# ============================================================
# GET — Buscar por ID
# ============================================================
@router.get("/{id_empregado}", response_model=EmpregadoResponse)
def buscar_empregado(id_empregado: int, db: Session = Depends(get_db)):
    emp = db.get(Empregado, id_empregado)
    if not emp:
        raise HTTPException(status_code=404,
                            detail="Empregado não encontrado.")
    return _serializar(emp, db)


# ============================================================
# PUT — Atualizar empregado
# ============================================================
@router.put("/{id_empregado}", response_model=EmpregadoResponse)
def atualizar_empregado(
    id_empregado: int,
    dados: EmpregadoUpdate,
    db: Session = Depends(get_db),
):
    emp = db.get(Empregado, id_empregado)
    if not emp:
        raise HTTPException(status_code=404,
                            detail="Empregado não encontrado.")

    if (dados.id_supervisor is not None
            and dados.id_supervisor == id_empregado):
        raise HTTPException(
            status_code=400,
            detail="RN-10: Empregado não pode ser seu próprio supervisor.")

    if dados.id_supervisor is not None:
        sup = db.get(Empregado, dados.id_supervisor)
        if not sup:
            raise HTTPException(status_code=400,
                                detail="Supervisor não encontrado.")

    if dados.matricula and dados.matricula != emp.matricula:
        if db.query(Empregado).filter(
                Empregado.matricula == dados.matricula).first():
            raise HTTPException(status_code=409,
                                detail="Matrícula já cadastrada.")

    if dados.cpf and dados.cpf != emp.cpf:
        if db.query(Empregado).filter(
                Empregado.cpf == dados.cpf).first():
            raise HTTPException(status_code=409,
                                detail="CPF já cadastrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(emp, campo, valor)

    db.commit()
    db.refresh(emp)
    return _serializar(emp, db)


# ============================================================
# DELETE — Excluir empregado
# ============================================================
@router.delete("/{id_empregado}", status_code=204)
def deletar_empregado(id_empregado: int, db: Session = Depends(get_db)):
    emp = db.get(Empregado, id_empregado)
    if not emp:
        raise HTTPException(status_code=404,
                            detail="Empregado não encontrado.")
    db.delete(emp)
    db.commit()
