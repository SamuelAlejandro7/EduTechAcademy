from decimal import Decimal

import pytest

from src.Domain.errors import CantidadInvalida, ImporteInvalido
from src.Domain.value_objects import Cantidad, Dinero, EstadoOperacion


def test_dinero_usa_decimal_y_dos_decimales():
    assert Dinero.de("10.005").monto == Decimal("10.01")
    assert Dinero.de(566).monto == Decimal("566.00")


def test_dinero_evita_error_binario_de_float():
    # 0.1 + 0.2 != 0.3 con float; con Dinero sí es exacto
    assert Dinero.de("0.10") + Dinero.de("0.20") == Dinero.de("0.30")


@pytest.mark.parametrize("valor", [1.5, True, "abc", -1, "-0.01"])
def test_dinero_rechaza_valores_invalidos(valor):
    with pytest.raises(ImporteInvalido):
        Dinero.de(valor)


def test_dinero_monto_debe_ser_decimal():
    with pytest.raises(ImporteInvalido):
        Dinero(10)  # type: ignore[arg-type]


def test_dinero_operaciones_y_orden():
    assert Dinero.de(100).por(3) == Dinero.de(300)
    assert Dinero.de(100).por(Cantidad(2)) == Dinero.de(200)
    assert Dinero.de(1000).porcentaje(50) == Dinero.de(500)
    assert Dinero.de("1499.99") < Dinero.de(1500)
    assert Dinero.de(1500) >= Dinero.de(1500)
    assert str(Dinero.de(5)) == "5.00 MXN"


def test_dinero_no_mezcla_monedas():
    with pytest.raises(ImporteInvalido):
        Dinero.de(1, "MXN") + Dinero.de(1, "USD")
    with pytest.raises(ImporteInvalido):
        assert Dinero.de(1, "MXN") < Dinero.de(1, "USD")


@pytest.mark.parametrize("factor", [-1, True, 1.5])
def test_dinero_por_rechaza_factor_invalido(factor):
    with pytest.raises(CantidadInvalida):
        Dinero.de(10).por(factor)


@pytest.mark.parametrize("valor", [0, -3, 1.5, "2", True])
def test_cantidad_debe_ser_entero_positivo(valor):
    with pytest.raises(CantidadInvalida):
        Cantidad(valor)


def test_cantidad_suma():
    assert Cantidad(2) + Cantidad(3) == Cantidad(5)


def test_estados_terminales():
    assert EstadoOperacion.FINALIZADA.es_terminal
    assert EstadoOperacion.CANCELADA.es_terminal
    assert not EstadoOperacion.SOLICITADA.es_terminal
