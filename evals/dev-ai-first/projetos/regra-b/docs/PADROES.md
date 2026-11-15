# Padrões do time

Conferidos na revisão de código.

- Dinheiro é sempre `int` em centavos (`app/dinheiro.py`).
- Erro de regra de negócio herda de `ErroDeDominio` (`app/erros.py`).
- Toda regra de desconto nova registra o motivo com `auditoria.registrar_desconto(pedido_id, codigo, motivo)` (`app/auditoria.py`) quando o desconto é aplicado. As regras antigas ainda não migraram; não as altere.
