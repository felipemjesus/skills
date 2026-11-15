"""Trilha de auditoria de descontos. Em memória aqui; em produção grava na tabela de auditoria."""

REGISTROS = []


def registrar_desconto(pedido_id: str, codigo: str, motivo: str) -> None:
    REGISTROS.append({"pedido": pedido_id, "cupom": codigo, "motivo": motivo})
