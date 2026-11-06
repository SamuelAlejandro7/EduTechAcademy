"""Patrón Specification: reglas de negocio como objetos componibles (AND / OR / NOT).

Cada regla simple es una clase con una sola responsabilidad. Las reglas del negocio
(``puede_procesarse``, ``beneficio_referencia``...) se arman combinando reglas simples
con los operadores ``&`` (AND), ``|`` (OR) y ``~`` (NOT).

Además de decir si se cumple, ``explicar`` devuelve QUÉ condiciones fallaron, para poder
reportar motivos concretos en errores y en la evidencia de los casos de prueba.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.Domain.value_objects import Dinero

if TYPE_CHECKING:  # solo para anotaciones; evita importaciones circulares
    from src.Domain.entities import Actor, Operacion, RecursoFormativo

UMBRAL_BENEFICIO = Dinero.de(1500)
PORCENTAJE_ANTICIPO = 50


@dataclass(frozen=True)
class ContextoEvaluacion:
    """Datos sobre los que se evalúan las reglas."""

    operacion: Operacion
    actor: Actor | None = None
    recursos: Mapping[str, RecursoFormativo] = field(default_factory=dict)
    monto_pagado: Dinero | None = None


class Specification(ABC):
    descripcion: str = "regla"

    @abstractmethod
    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool: ...

    def explicar(self, ctx: ContextoEvaluacion) -> tuple[str, ...]:
        """Condiciones que no se cumplen (vacío si la regla se cumple)."""
        return () if self.is_satisfied_by(ctx) else (self.descripcion,)

    def __and__(self, otra: Specification) -> Specification:
        return And(self, otra)

    def __or__(self, otra: Specification) -> Specification:
        return Or(self, otra)

    def __invert__(self) -> Specification:
        return Not(self)


# --- Combinadores -------------------------------------------------------------
class And(Specification):
    def __init__(self, izquierda: Specification, derecha: Specification) -> None:
        self.izquierda, self.derecha = izquierda, derecha
        self.descripcion = f"({izquierda.descripcion} AND {derecha.descripcion})"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return self.izquierda.is_satisfied_by(ctx) and self.derecha.is_satisfied_by(ctx)

    def explicar(self, ctx: ContextoEvaluacion) -> tuple[str, ...]:
        return self.izquierda.explicar(ctx) + self.derecha.explicar(ctx)


class Or(Specification):
    def __init__(self, izquierda: Specification, derecha: Specification) -> None:
        self.izquierda, self.derecha = izquierda, derecha
        self.descripcion = f"({izquierda.descripcion} OR {derecha.descripcion})"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return self.izquierda.is_satisfied_by(ctx) or self.derecha.is_satisfied_by(ctx)

    def explicar(self, ctx: ContextoEvaluacion) -> tuple[str, ...]:
        if self.is_satisfied_by(ctx):
            return ()
        return (f"ninguna de: {self.izquierda.descripcion} / {self.derecha.descripcion}",)


class Not(Specification):
    def __init__(self, interna: Specification) -> None:
        self.interna = interna
        self.descripcion = f"NOT({interna.descripcion})"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return not self.interna.is_satisfied_by(ctx)


# --- Reglas simples -----------------------------------------------------------
class ActorActivo(Specification):
    descripcion = "actor activo"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return ctx.actor is not None and ctx.actor.activo


class OperacionConLineas(Specification):
    descripcion = "operación con al menos una línea"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return len(ctx.operacion.lineas) > 0


class OperacionAutorizada(Specification):
    descripcion = "operación autorizada"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return ctx.operacion.autorizado


class ActorPreferente(Specification):
    descripcion = "actor preferente"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return ctx.actor is not None and ctx.actor.es_preferente


class TotalMinimo(Specification):
    def __init__(self, minimo: Dinero = UMBRAL_BENEFICIO) -> None:
        self.minimo = minimo
        self.descripcion = f"total >= {minimo}"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return ctx.operacion.total() >= self.minimo


class PromocionActiva(Specification):
    descripcion = "promoción activa"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return ctx.operacion.promocion_activa


class RecursosHabilitados(Specification):
    descripcion = "todos los recursos existen y están habilitados"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        return all(
            (r := ctx.recursos.get(linea.recurso_id)) is not None and r.habilitado
            for linea in ctx.operacion.lineas
        )


class CapacidadDisponible(Specification):
    descripcion = "hay cupo suficiente en todos los recursos"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        pedido: dict[str, int] = defaultdict(int)
        for linea in ctx.operacion.lineas:
            pedido[linea.recurso_id] += linea.cantidad.valor
        return all(
            (r := ctx.recursos.get(rid)) is not None and cantidad <= r.capacidad
            for rid, cantidad in pedido.items()
        )


class AnticipoMinimoCubierto(Specification):
    """Regla del BRD de EduTech: anticipo mínimo del 50 % del total (RN-01)."""

    def __init__(self, porcentaje: int = PORCENTAJE_ANTICIPO) -> None:
        self.porcentaje = porcentaje
        self.descripcion = f"anticipo >= {porcentaje}% del total"

    def is_satisfied_by(self, ctx: ContextoEvaluacion) -> bool:
        if ctx.monto_pagado is None:
            return False
        return ctx.monto_pagado >= ctx.operacion.total().porcentaje(self.porcentaje)


# --- Reglas de negocio nombradas ---------------------------------------------
def puede_procesarse() -> Specification:
    """actor activo AND operación con al menos una línea AND autorización."""
    return ActorActivo() & OperacionConLineas() & OperacionAutorizada()


def beneficio_referencia(umbral: Dinero = UMBRAL_BENEFICIO) -> Specification:
    """actor preferente AND total >= 1500 MXN AND NOT promoción activa."""
    return ActorPreferente() & TotalMinimo(umbral) & ~PromocionActiva()


def puede_inscribirse(exigir_anticipo: bool = False) -> Specification:
    """recursos habilitados AND cupo disponible [AND anticipo mínimo del BRD]."""
    regla = RecursosHabilitados() & CapacidadDisponible()
    return regla & AnticipoMinimoCubierto() if exigir_anticipo else regla
