"""Entidades y agregado del dominio.

* ``Operacion`` es la raíz del agregado; ``LineaOperacion`` solo existe dentro de ella.
* ``Actor`` y ``RecursoFormativo`` son agregados independientes que se referencian por id.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone

from src.Domain import events as ev
from src.Domain.errors import (
    CantidadInvalida,
    CapacidadInsuficiente,
    InscripcionNoPermitida,
    OperacionNoModificable,
    OperacionNoProcesable,
    RecursoNoHabilitado,
)
from src.Domain.specifications import (
    ContextoEvaluacion,
    beneficio_referencia,
    puede_inscribirse,
    puede_procesarse,
)
from src.Domain.state_machine import Accion, siguiente_estado
from src.Domain.value_objects import Cantidad, Dinero, EstadoOperacion


def _ahora(ahora: datetime | None) -> datetime:
    return ahora or datetime.now(timezone.utc)


@dataclass
class Actor:
    """Quien solicita operaciones (en EduTech: el alumno)."""

    actor_id: str
    nombre: str
    es_preferente: bool = False
    activo: bool = True
    ciudad: str = ""


@dataclass
class RecursoFormativo:
    """Programa formativo del catálogo, con precio y cupo."""

    recurso_id: str
    descripcion: str
    precio: Dinero
    capacidad: int
    habilitado: bool = True

    def __post_init__(self) -> None:
        if (
            not isinstance(self.capacidad, int)
            or isinstance(self.capacidad, bool)
            or self.capacidad < 0
        ):
            raise CantidadInvalida(f"capacidad no válida: {self.capacidad!r}")

    def tiene_cupo(self, cantidad: Cantidad) -> bool:
        return self.habilitado and cantidad.valor <= self.capacidad

    def reservar(self, cantidad: Cantidad) -> None:
        if not self.habilitado:
            raise RecursoNoHabilitado(f"el recurso {self.recurso_id} no está habilitado")
        if cantidad.valor > self.capacidad:
            raise CapacidadInsuficiente(
                f"cupo insuficiente en {self.recurso_id}",
                (f"solicitado {cantidad.valor}, disponible {self.capacidad}",),
            )
        self.capacidad -= cantidad.valor


@dataclass(frozen=True)
class LineaOperacion:
    """Renglón de una operación. Guarda el precio vigente al solicitar (snapshot)."""

    recurso_id: str
    precio_unitario: Dinero
    cantidad: Cantidad

    def subtotal(self) -> Dinero:
        return self.precio_unitario.por(self.cantidad)


class Operacion:
    """Raíz del agregado: solicitud de inscripción a uno o más programas."""

    def __init__(
        self,
        operacion_id: str,
        actor_id: str,
        fecha_solicitud: datetime,
        promocion_activa: bool = False,
        autorizado: bool = False,
        referencia: str = "",
        estado: EstadoOperacion = EstadoOperacion.SOLICITADA,
        lineas: list[LineaOperacion] | None = None,
    ) -> None:
        self.operacion_id = operacion_id
        self.actor_id = actor_id
        self.fecha_solicitud = fecha_solicitud
        self.promocion_activa = promocion_activa
        self.autorizado = autorizado
        self.referencia = referencia
        self.estado = estado
        self.lineas: list[LineaOperacion] = list(lineas or [])
        self._eventos: list[ev.EventoDeDominio] = []

    # -- Consultas --------------------------------------------------------------
    def total(self) -> Dinero:
        resultado = Dinero.cero()
        for linea in self.lineas:
            resultado = resultado + linea.subtotal()
        return resultado

    def pull_events(self) -> list[ev.EventoDeDominio]:
        """Entrega y limpia los eventos pendientes (los publica la capa de aplicación)."""
        pendientes, self._eventos = self._eventos, []
        return pendientes

    # -- Líneas -----------------------------------------------------------------
    def agregar_linea(self, recurso: RecursoFormativo, cantidad: int | Cantidad) -> LineaOperacion:
        """Agrega (o suma) una línea validando estado, habilitación y cupo."""
        if self.estado is not EstadoOperacion.SOLICITADA:
            raise OperacionNoModificable(
                f"solo se pueden editar líneas en estado SOLICITADA (actual: {self.estado.value})"
            )
        cantidad = cantidad if isinstance(cantidad, Cantidad) else Cantidad(cantidad)
        if not recurso.habilitado:
            raise RecursoNoHabilitado(f"el recurso {recurso.recurso_id} no está habilitado")
        existente = next((x for x in self.lineas if x.recurso_id == recurso.recurso_id), None)
        total_pedido = cantidad + existente.cantidad if existente else cantidad
        if total_pedido.valor > recurso.capacidad:
            raise CapacidadInsuficiente(
                f"cupo insuficiente en {recurso.recurso_id}",
                (f"solicitado {total_pedido.valor}, disponible {recurso.capacidad}",),
            )
        nueva = LineaOperacion(recurso.recurso_id, recurso.precio, total_pedido)
        if existente:
            self.lineas[self.lineas.index(existente)] = nueva
        else:
            self.lineas.append(nueva)
        return nueva

    # -- Transiciones -----------------------------------------------------------
    def aceptar(self, actor: Actor, ahora: datetime | None = None) -> None:
        """SOLICITADA -> ACEPTADA. Exige ``puede_procesarse``."""
        destino = siguiente_estado(self.estado, Accion.ACEPTAR)
        ctx = ContextoEvaluacion(operacion=self, actor=actor)
        regla = puede_procesarse()
        if not regla.is_satisfied_by(ctx):
            raise OperacionNoProcesable("la operación no puede procesarse", regla.explicar(ctx))
        momento = _ahora(ahora)
        self.estado = destino
        self._eventos.append(ev.OperacionAceptada(self.operacion_id, momento, actor.actor_id))
        if beneficio_referencia().is_satisfied_by(ctx):
            self._eventos.append(
                ev.BeneficioReferenciaOtorgado(
                    self.operacion_id, momento, actor.actor_id, self.total()
                )
            )

    def inscribir(
        self,
        recursos: Mapping[str, RecursoFormativo],
        monto_pagado: Dinero | None = None,
        ahora: datetime | None = None,
    ) -> None:
        """ACEPTADA -> INSCRITA. Valida recursos y cupo (y el anticipo del BRD si se informa pago)
        y reserva el cupo de cada recurso."""
        destino = siguiente_estado(self.estado, Accion.INSCRIBIR)
        ctx = ContextoEvaluacion(operacion=self, recursos=recursos, monto_pagado=monto_pagado)
        regla = puede_inscribirse(exigir_anticipo=monto_pagado is not None)
        if not regla.is_satisfied_by(ctx):
            raise InscripcionNoPermitida("la operación no puede inscribirse", regla.explicar(ctx))
        for linea in self.lineas:
            recursos[linea.recurso_id].reservar(linea.cantidad)
        self.estado = destino
        self._eventos.append(ev.OperacionInscrita(self.operacion_id, _ahora(ahora), self.total()))

    def finalizar(self, ahora: datetime | None = None) -> None:
        """INSCRITA -> FINALIZADA."""
        self.estado = siguiente_estado(self.estado, Accion.FINALIZAR)
        self._eventos.append(ev.OperacionFinalizada(self.operacion_id, _ahora(ahora)))

    def cancelar(
        self, motivo: str = "cancelada por el solicitante", ahora: datetime | None = None
    ) -> None:
        """SOLICITADA -> CANCELADA."""
        self.estado = siguiente_estado(self.estado, Accion.CANCELAR)
        self._eventos.append(ev.OperacionCancelada(self.operacion_id, _ahora(ahora), motivo))
