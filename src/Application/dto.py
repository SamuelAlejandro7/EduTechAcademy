"""DTOs de entrada y salida de los casos de uso.

Los importes viajan como ``Decimal`` (no ``float``). La capa API decide cómo serializarlos
(se recomienda string o número con dos decimales).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.Domain.entities import Operacion
from src.Domain.state_machine import Accion


@dataclass(frozen=True)
class LineaSolicitada:
    recurso_id: str
    cantidad: int


@dataclass(frozen=True)
class SolicitarOperacionCommand:
    operacion_id: str
    actor_id: str
    lineas: tuple[LineaSolicitada, ...]
    referencia: str = ""
    promocion_activa: bool = False
    autorizado: bool = False
    fecha_solicitud: datetime | None = None


@dataclass(frozen=True)
class AplicarAccionCommand:
    operacion_id: str
    accion: Accion
    monto_pagado: Decimal | None = None  # si se informa, se exige el anticipo mínimo del BRD
    motivo: str | None = None  # solo para CANCELAR


@dataclass(frozen=True)
class LineaDTO:
    recurso_id: str
    precio_unitario: Decimal
    cantidad: int
    subtotal: Decimal


@dataclass(frozen=True)
class OperacionDTO:
    operacion_id: str
    actor_id: str
    estado: str
    referencia: str
    promocion_activa: bool
    autorizado: bool
    total: Decimal
    moneda: str
    lineas: tuple[LineaDTO, ...] = field(default_factory=tuple)

    @classmethod
    def desde_dominio(cls, op: Operacion) -> OperacionDTO:
        lineas = tuple(
            LineaDTO(x.recurso_id, x.precio_unitario.monto, x.cantidad.valor, x.subtotal().monto)
            for x in op.lineas
        )
        return cls(
            op.operacion_id,
            op.actor_id,
            op.estado.value,
            op.referencia,
            op.promocion_activa,
            op.autorizado,
            op.total().monto,
            op.total().moneda,
            lineas,
        )


@dataclass(frozen=True)
class ResultadoRegla:
    """Resultado de evaluar una regla (``puede_procesarse`` o ``beneficio_referencia``)."""

    operacion_id: str
    regla: str
    cumple: bool
    total: Decimal
    motivos_incumplidos: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultadoTransicion:
    operacion_id: str
    estado_inicial: str
    estado_final: str
    eventos: tuple[str, ...] = ()
