import unittest

from app.erros import ErroDeDominio, PedidoNaoEncontrado
from app.pedidos import Pedido
from app.repositorio import RepositorioDePedidos


class Repositorio(unittest.TestCase):
    def test_salva_e_busca(self):
        repo = RepositorioDePedidos()
        repo.salvar(Pedido(id="p1"))
        self.assertEqual(repo.buscar("p1").id, "p1")

    def test_inexistente_e_erro_de_dominio(self):
        with self.assertRaises(PedidoNaoEncontrado) as ctx:
            RepositorioDePedidos().buscar("nada")
        self.assertIsInstance(ctx.exception, ErroDeDominio)


if __name__ == "__main__":
    unittest.main()
