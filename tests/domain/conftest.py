from datetime import datetime, timezone

import pytest

from src.Domain.entities import Actor, Operacion, RecursoFormativo
from src.Domain.value_objects import Dinero

AHORA = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def actor():
    return Actor("A1", "Alumno 1", es_preferente=False, activo=True, ciudad="Monterrey")


@pytest.fixture
def preferente():
    return Actor("A2", "Alumno 2", es_preferente=True, activo=True, ciudad="Monterrey")


@pytest.fixture
def recurso():
    return RecursoFormativo("P1", "Cloud 01", Dinero.de(800), capacidad=10, habilitado=True)


@pytest.fixture
def recurso_caro():
    return RecursoFormativo("P2", "Data 02", Dinero.de(1000), capacidad=5, habilitado=True)


@pytest.fixture
def operacion(recurso):
    op = Operacion("O1", "A1", AHORA, autorizado=True, referencia="PIA_1")
    op.agregar_linea(recurso, 1)
    return op
