from app.dinheiro import formatar
from app.pedidos import total


def linhas(pedidos):
    saida = []
    for p in pedidos:
        saida.append(f"{p.id};{total(p)}")
    return saida


def linhas_formatadas(pedidos):
    saida = []
    for p in pedidos:
        saida.append(f"{p.id};{formatar(total(p))}")
    return saida
