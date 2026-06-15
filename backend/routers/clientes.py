"""Router: Clientes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.cliente import Cliente
from backend.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate
from backend.services.validacoes import validar_cnpj

router = APIRouter(prefix="/clientes", tags=["Clientes"])


# ─────────────────────────────────────────────
#  POST /clientes/
# ─────────────────────────────────────────────
@router.post("/", response_model=ClienteResponse, status_code=201)
def criar_cliente(dados: ClienteCreate, db: Session = Depends(get_db)):
    """Cadastra novo cliente.

    RN-01: Apenas PJ (CNPJ) — CPF é bloqueado no schema.
    RN-02: CNPJ e e-mail devem ser únicos.
    """
    cnpj = validar_cnpj(dados.cnpj)

    if db.query(Cliente).filter(Cliente.cnpj == cnpj).first():
        raise HTTPException(status_code=409, detail="CNPJ já cadastrado.")

    if db.query(Cliente).filter(Cliente.email == dados.email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    cliente = Cliente(
        cnpj=cnpj,
        razao_social=dados.razao_social,
        nome_fantasia=dados.nome_fantasia,
        email=dados.email,
        telefone=dados.telefone,
        cep=dados.cep,
        logradouro=dados.logradouro,
        numero=dados.numero,
        complemento=dados.complemento,
        bairro=dados.bairro,
        cidade=dados.cidade,
        estado=dados.estado,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


# ─────────────────────────────────────────────
#  GET /clientes/
# ─────────────────────────────────────────────
@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retorna lista paginada de clientes."""
    return db.query(Cliente).offset(skip).limit(limit).all()


# ─────────────────────────────────────────────
#  GET /clientes/{id_cliente}
# ─────────────────────────────────────────────
@router.get("/{id_cliente}", response_model=ClienteResponse)
def buscar_cliente(id_cliente: int, db: Session = Depends(get_db)):
    """Retorna um cliente pelo ID."""
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente


# ─────────────────────────────────────────────
#  PUT /clientes/{id_cliente}
# ─────────────────────────────────────────────
@router.put("/{id_cliente}", response_model=ClienteResponse)
def atualizar_cliente(
    id_cliente: int,
    dados: ClienteUpdate,
    db: Session = Depends(get_db),
):
    """Atualiza dados de um cliente existente.

    RN-02: CNPJ não pode ser alterado (identificador único).
             E-mail continua sendo validado para unicidade.
    Apenas os campos enviados no payload são atualizados (partial update).
    """
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # Extrai apenas os campos que foram realmente enviados no payload
    campos_enviados = dados.model_dump(exclude_unset=True)

    if not campos_enviados:
        raise HTTPException(
            status_code=422,
            detail="Nenhum campo foi enviado para atualização.",
        )

    # Valida unicidade do e-mail se ele estiver sendo alterado
    if "email" in campos_enviados:
        email_duplicado = (
            db.query(Cliente)
            .filter(
                Cliente.email == campos_enviados["email"],
                Cliente.id_cliente != id_cliente,
            )
            .first()
        )
        if email_duplicado:
            raise HTTPException(
                status_code=409,
                detail="E-mail já pertence a outro cliente.",
            )

    # Aplica os campos no modelo — CNPJ nunca está em campos_enviados (RN-02)
    for campo, valor in campos_enviados.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return cliente


# ─────────────────────────────────────────────
#  DELETE /clientes/{id_cliente}
# ─────────────────────────────────────────────
@router.delete("/{id_cliente}", status_code=204)
def deletar_cliente(id_cliente: int, db: Session = Depends(get_db)):
    """Remove um cliente pelo ID."""
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    db.delete(cliente)
    db.commit()
