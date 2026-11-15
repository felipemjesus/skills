"""Dinheiro é sempre int em centavos. Nunca use float para valor monetário."""


def formatar(centavos: int) -> str:
    reais, resto = divmod(centavos, 100)
    return f"R$ {reais},{resto:02d}"
