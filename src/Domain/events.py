"""Domain Events: hechos ya ocurridos en el dominio, inmutables y en pasado."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.Domain.value_objects import Dinero


@dataclass(frozen=True)
class EventoDeDominio:
    operacion_id: str
    ocurrido_en: datetime

    @property
    def nombre(self) -> str:
        return type(self).__name__


@dataclass(frozen=True)
class OperacionAceptada(EventoDeDominio):
    actor_id: str = ""


@dataclass(frozen=True)
class BeneficioReferenciaOtorgado(EventoDeDominio):
    """Se emite al aceptar una operación que cumple ``beneficio_referencia``."""

    actor_id: str = ""
    total: Dinero = field(default_factory=Dinero.cero)


@dataclass(frozen=True)
class OperacionInscrita(EventoDeDominio):
    total: Dinero = field(default_factory=Dinero.cero)


@dataclass(frozen=True)
class OperacionFinalizada(EventoDeDominio):
    pass


@dataclass(frozen=True)
class OperacionCancelada(EventoDeDominio):
    motivo: str = ""
