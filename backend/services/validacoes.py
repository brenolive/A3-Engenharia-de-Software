"""
Serviço de Validações — Regras de Negócio.
Camada de Aplicação / Serviços.
"""

import re

from fastapi import HTTPException


# ── CNPJ ────────────────────────────────────────────────────

def validar_cnpj(cnpj: str) -> str:
    """
    RN-01: Valida CNPJ e bloqueia CPF.
    Retorna CNPJ formatado: XX.XXX.XXX/XXXX-XX
    """
    apenas_digitos = re.sub(r"\D", "", cnpj)

    if len(apenas_digitos) == 11:
        raise HTTPException(
            status_code=422,
            detail={
                "erro": "CNPJ_INVALIDO",
                "mensagem": (
                    "CPF não é aceito. "
                    "O sistema atende apenas Pessoas Jurídicas (CNPJ com 14 dígitos)."
                ),
            },
        )

    if len(apenas_digitos) != 14:
        raise HTTPException(
            status_code=422,
            detail={
                "erro": "CNPJ_INVALIDO",
                "mensagem": "CNPJ deve conter 14 dígitos.",
            },
        )

    # Valida dígitos verificadores
    def calc_digito(parcial: str, pesos: list) -> int:
        soma = sum(int(d) * p for d, p in zip(parcial, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    d1 = calc_digito(apenas_digitos[:12], pesos1)
    d2 = calc_digito(apenas_digitos[:13], pesos2)

    if int(apenas_digitos[12]) != d1 or int(apenas_digitos[13]) != d2:
        raise HTTPException(
            status_code=422,
            detail={
                "erro": "CNPJ_INVALIDO",
                "mensagem": "CNPJ com dígitos verificadores inválidos.",
            },
        )

    d = apenas_digitos
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:14]}"


# ── Encomenda ────────────────────────────────────────────────

def calcular_valores_encomenda(itens: list, desconto_percentual: float) -> dict:
    """
    RN-06: Calcula valor_bruto e valor_liquido da encomenda.
    valor_liquido = valor_bruto × (1 - desconto / 100)
    """
    valor_bruto = sum(
        item["quantidade"] * item["preco_unitario"] for item in itens
    )
    valor_liquido = round(valor_bruto * (1 - desconto_percentual / 100), 2)
    return {
        "valor_bruto": round(valor_bruto, 2),
        "valor_liquido": valor_liquido,
    }


def gerar_numero_encomenda(ultimo_id: int) -> str:
    """
    RN-07: Gera número único da encomenda.
    Formato: ENC-YYYYMMDD-NNNNNN
    """
    from datetime import date
    hoje = date.today().strftime("%Y%m%d")
    seq = str(ultimo_id + 1).zfill(6)
    return f"ENC-{hoje}-{seq}"


# ── Componente ───────────────────────────────────────────────

def validar_componente_e_maquina(tipo_componente: str) -> None:
    """
    RN-08: Manutenção só pode ser registrada para MAQUINA.
    """
    if tipo_componente != "MAQUINA":
        raise HTTPException(
            status_code=422,
            detail={
                "erro": "COMPONENTE_INVALIDO",
                "mensagem": (
                    "Manutenção só pode ser registrada para "
                    "componentes do tipo MAQUINA."
                ),
            },
        )
