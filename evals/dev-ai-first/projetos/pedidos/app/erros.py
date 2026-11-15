class ErroDeDominio(Exception):
    """Base de todo erro de regra de negócio. A camada HTTP traduz em 422."""


class PedidoNaoEncontrado(ErroDeDominio):
    pass


class CupomInvalido(ErroDeDominio):
    pass
