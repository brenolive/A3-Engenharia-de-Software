"""Router: Componentes (Generalização + Especializações)."""

from typing import List


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.componente import (
    Componente, Ferramenta, Maquina, MaterialDiverso, MateriaPrima,
)
from backend.schemas.componente import ComponenteCreate, ComponenteResponse, ComponenteUpdate

router = APIRouter(prefix="/componentes", tags=["Componentes"])


@router.post("/", response_model=ComponenteResponse, status_code=201)
def criar_componente(dados: ComponenteCreate, db: Session = Depends(get_db)):
    """Cria componente e sua especialização correspondente."""
    comp = Componente(
        nome=dados.nome,
        descricao=dados.descricao,
        tipo_componente=dados.tipo_componente,
    )
    db.add(comp)
    db.flush()  # Gera id_componente antes da especialização

    tipo = dados.tipo_componente

    if tipo == "MATERIA_PRIMA":
        db.add(MateriaPrima(
            id_componente=comp.id_componente,
            origem=dados.origem,
            tipo_madeira=dados.tipo_madeira,
            certificacao=dados.certificacao,
        ))

    elif tipo == "MATERIAL_DIVERSO":
        db.add(MaterialDiverso(
            id_componente=comp.id_componente,
            categoria=dados.categoria,
            marca=dados.marca,
        ))

    elif tipo == "MAQUINA":
        db.add(Maquina(
            id_componente=comp.id_componente,
            modelo=dados.modelo,
            fabricante=dados.fabricante,
            numero_serie=dados.numero_serie,
            tempo_medio_vida=dados.tempo_medio_vida,
            data_compra=dados.data_compra,
            data_fim_garantia=dados.data_fim_garantia,
        ))

    elif tipo == "FERRAMENTA":
        db.add(Ferramenta(
            id_componente=comp.id_componente,
            tipo_ferramenta=dados.tipo_ferramenta,
            marca=dados.marca,
            numero_serie=dados.numero_serie,
        ))

    db.commit()
    db.refresh(comp)
    return comp


@router.get("/", response_model=List[ComponenteResponse])
def listar_componentes(
    tipo: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Componente)
    if tipo:
        q = q.filter(Componente.tipo_componente == tipo.upper())
    return q.all()


@router.get("/{id_componente}", response_model=ComponenteResponse)
def buscar_componente(id_componente: int, db: Session = Depends(get_db)):
    c = db.query(Componente).filter(
        Componente.id_componente == id_componente
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Componente não encontrado.")
    return c


@router.delete("/{id_componente}", status_code=204)
def deletar_componente(id_componente: int, db: Session = Depends(get_db)):
    c = db.query(Componente).filter(
        Componente.id_componente == id_componente
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Componente não encontrado.")
    db.delete(c)
    db.commit()


@router.put("/{id_componente}", response_model=ComponenteResponse)
def atualizar_componente(
    id_componente: int,
    dados: ComponenteUpdate,
    db: Session = Depends(get_db),
):
    c = db.query(Componente).filter(
        Componente.id_componente == id_componente
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Componente não encontrado.")

    # Atualiza campos base do componente
    for campo, valor in dados.model_dump(exclude_unset=True, exclude={
        "origem", "tipo_madeira", "certificacao",   # MateriaPrima
        "categoria", "marca",                        # MaterialDiverso / Ferramenta
        "modelo", "fabricante", "numero_serie",      # Maquina / Ferramenta
        "tempo_medio_vida", "data_compra",           # Maquina
        "data_fim_garantia", "tipo_ferramenta",      # Maquina / Ferramenta
    }).items():
        setattr(c, campo, valor)

    # Atualiza especialização conforme tipo atual
    tipo = c.tipo_componente

    if tipo == "MATERIA_PRIMA":
        esp = db.query(MateriaPrima).filter(
            MateriaPrima.id_componente == id_componente
        ).first()
        if esp:
            if dados.origem        is not None: esp.origem        = dados.origem
            if dados.tipo_madeira  is not None: esp.tipo_madeira  = dados.tipo_madeira
            if dados.certificacao  is not None: esp.certificacao  = dados.certificacao

    elif tipo == "MATERIAL_DIVERSO":
        esp = db.query(MaterialDiverso).filter(
            MaterialDiverso.id_componente == id_componente
        ).first()
        if esp:
            if dados.categoria is not None: esp.categoria = dados.categoria
            if dados.marca     is not None: esp.marca     = dados.marca

    elif tipo == "MAQUINA":
        esp = db.query(Maquina).filter(
            Maquina.id_componente == id_componente
        ).first()
        if esp:
            if dados.modelo           is not None: esp.modelo           = dados.modelo
            if dados.fabricante       is not None: esp.fabricante       = dados.fabricante
            if dados.numero_serie     is not None: esp.numero_serie     = dados.numero_serie
            if dados.tempo_medio_vida is not None: esp.tempo_medio_vida = dados.tempo_medio_vida
            if dados.data_compra      is not None: esp.data_compra      = dados.data_compra
            if dados.data_fim_garantia is not None: esp.data_fim_garantia = dados.data_fim_garantia

    elif tipo == "FERRAMENTA":
        esp = db.query(Ferramenta).filter(
            Ferramenta.id_componente == id_componente
        ).first()
        if esp:
            if dados.tipo_ferramenta is not None: esp.tipo_ferramenta = dados.tipo_ferramenta
            if dados.marca           is not None: esp.marca           = dados.marca
            if dados.numero_serie    is not None: esp.numero_serie    = dados.numero_serie

    db.commit()
    db.refresh(c)
    return c