from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from app.dinheiro import formatar
from app.erros import CupomInvalido


@dataclass(frozen=True)
class Cupom:
    codigo: str
    tipo: str  # "percentual" ou "fixo"
    valor: int  # percentual: 0 a 100; fixo: centavos
    validade: Optional[date] = None  # último dia em que o cupom vale; None = sem validade


@dataclass
class Item:
    sku: str
    quantidade: int
    preco_unitario: int  # centavos


@dataclass
class Pedido:
    id: str
    itens: list = field(default_factory=list)
    cupom: Optional[Cupom] = None


def subtotal(pedido: Pedido) -> int:
    return sum(i.quantidade * i.preco_unitario for i in pedido.itens)


def total(pedido: Pedido, hoje: Optional[date] = None) -> int:
    hoje = hoje or date.today()
    bruto = subtotal(pedido)
    cupom = pedido.cupom
    if cupom is None:
        return bruto
    if cupom.tipo == "percentual":
        if not 0 <= cupom.valor <= 100:
            raise CupomInvalido(f"percentual fora de 0 a 100: {cupom.valor}")
        return bruto - bruto * cupom.valor // 100
    if cupom.tipo == "fixo":
        return bruto - cupom.valor
    raise CupomInvalido(f"tipo de cupom desconhecido: {cupom.tipo}")


def resumo(pedido: Pedido) -> str:
    return f"Pedido {pedido.id}: {formatar(total(pedido))}"
