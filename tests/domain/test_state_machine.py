import pytest

from src.Domain.errors import TransicionInvalida
from src.Domain.state_machine import TRANSICIONES, Accion, acciones_permitidas, siguiente_estado
from src.Domain.value_objects import EstadoOperacion as E


@pytest.mark.parametrize(
    ("origen", "accion", "destino"),
    [
        (E.SOLICITADA, Accion.ACEPTAR, E.ACEPTADA),
        (E.ACEPTADA, Accion.INSCRIBIR, E.INSCRITA),
        (E.INSCRITA, Accion.FINALIZAR, E.FINALIZADA),
        (E.SOLICITADA, Accion.CANCELAR, E.CANCELADA),
    ],
)
def test_transiciones_validas(origen, accion, destino):
    assert siguiente_estado(origen, accion) is destino


def test_toda_combinacion_fuera_de_la_tabla_es_invalida():
    for estado in E:
        for accion in Accion:
            if (estado, accion) in TRANSICIONES:
                continue
            with pytest.raises(TransicionInvalida):
                siguiente_estado(estado, accion)


def test_estados_finales_no_permiten_acciones():
    assert acciones_permitidas(E.FINALIZADA) == ()
    assert acciones_permitidas(E.CANCELADA) == ()
    with pytest.raises(TransicionInvalida, match="estado final"):
        siguiente_estado(E.CANCELADA, Accion.ACEPTAR)


def test_acciones_permitidas_desde_solicitada():
    assert set(acciones_permitidas(E.SOLICITADA)) == {Accion.ACEPTAR, Accion.CANCELAR}
