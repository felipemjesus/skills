from app.erros import PedidoNaoEncontrado
from app.pedidos import Pedido


class RepositorioDePedidos:
    """Guarda em memória. O mesmo contrato é usado pelo repositório de banco."""

    def __init__(self):
        self._pedidos = {}

    def salvar(self, pedido: Pedido) -> None:
        self._pedidos[pedido.id] = pedido

    def buscar(self, id_pedido: str) -> Pedido:
        try:
            return self._pedidos[id_pedido]
        except KeyError:
            raise PedidoNaoEncontrado(id_pedido) from None
