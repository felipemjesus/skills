import unittest

from app.erros import CupomInvalido, ErroDeDominio
from app.pedidos import Cupom, Item, Pedido, resumo, total


def pedido(*itens, cupom=None):
    return Pedido(id="p1", itens=list(itens), cupom=cupom)


class TotalDoPedido(unittest.TestCase):
    def test_sem_cupom_soma_os_itens_em_centavos(self):
        self.assertEqual(total(pedido(Item("a", 2, 1050), Item("b", 1, 99))), 2199)

    def test_cupom_percentual(self):
        self.assertEqual(total(pedido(Item("a", 1, 1000), cupom=Cupom("DEZ", "percentual", 10))), 900)

    def test_cupom_fixo(self):
        self.assertEqual(total(pedido(Item("a", 1, 1000), cupom=Cupom("CINCO", "fixo", 500))), 500)

    def test_percentual_invalido_e_erro_de_dominio(self):
        with self.assertRaises(CupomInvalido) as ctx:
            total(pedido(Item("a", 1, 1000), cupom=Cupom("X", "percentual", 120)))
        self.assertIsInstance(ctx.exception, ErroDeDominio)

    def test_resumo_formata_em_reais(self):
        self.assertEqual(resumo(pedido(Item("a", 1, 1234))), "Pedido p1: R$ 12,34")


if __name__ == "__main__":
    unittest.main()
