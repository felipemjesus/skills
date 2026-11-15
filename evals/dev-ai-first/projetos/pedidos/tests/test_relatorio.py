import unittest

from app.pedidos import Item, Pedido
from app.relatorio import linhas


class Relatorio(unittest.TestCase):
    def test_gera_uma_linha_por_pedido(self):
        self.assertEqual(len(linhas([Pedido(id="p1", itens=[Item("a", 1, 100)])])), 1)


if __name__ == "__main__":
    unittest.main()
