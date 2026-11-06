"""Máquina de estados de la operación, dirigida por una tabla.

    SOLICITADA --aceptar--> ACEPTADA --inscribir--> INSCRITA --finalizar--> FINALIZADA
         \\--cancelar--> CANCELADA

Cualquier par (estado, acción) que no esté en la tabla es una transición inválida.
Agregar una regla nueva (p. ej. cancelar desde ACEPTADA) es agregar una fila.
"""

from __future__ import annotations

from enum import Enum

from src.Domain.errors import TransicionInvalida
from src.Domain.value_objects import EstadoOperacion as E


class Accion(str, Enum):
    ACEPTAR = "aceptar"
    INSCRIBIR = "inscribir"
    FINALIZAR = "finalizar"
    CANCELAR = "cancelar"


TRANSICIONES: dict[tuple[E, Accion], E] = {
    (E.SOLICITADA, Accion.ACEPTAR): E.ACEPTADA,
    (E.ACEPTADA, Accion.INSCRIBIR): E.INSCRITA,
    (E.INSCRITA, Accion.FINALIZAR): E.FINALIZADA,
    (E.SOLICITADA, Accion.CANCELAR): E.CANCELADA,
}


def acciones_permitidas(estado: E) -> tuple[Accion, ...]:
    return tuple(a for (e, a) in TRANSICIONES if e == estado)


def siguiente_estado(estado: E, accion: Accion) -> E:
    """Devuelve el estado destino o lanza ``TransicionInvalida``."""
    destino = TRANSICIONES.get((estado, accion))
    if destino is None:
        permitidas = (
            ", ".join(a.value for a in acciones_permitidas(estado)) or "ninguna (estado final)"
        )
        raise TransicionInvalida(
            f"no se puede '{accion.value}' una operación en estado {estado.value}",
            (f"acciones permitidas: {permitidas}",),
        )
    return destino
