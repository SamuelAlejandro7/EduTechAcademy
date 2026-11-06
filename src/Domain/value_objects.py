"""Value Objects del dominio: inmutables y comparados por valor."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from enum import Enum
from functools import total_ordering

from src.Domain.errors import CantidadInvalida, ImporteInvalido

_CENTAVOS = Decimal("0.01")


class EstadoOperacion(str, Enum):
    """Estados del ciclo de vida de una operación (flujo de referencia del PIA)."""

    SOLICITADA = "SOLICITADA"
    ACEPTADA = "ACEPTADA"
    INSCRITA = "INSCRITA"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"

    @property
    def es_terminal(self) -> bool:
        return self in (EstadoOperacion.FINALIZADA, EstadoOperacion.CANCELADA)


@total_ordering
@dataclass(frozen=True)
class Dinero:
    """Importe monetario con ``Decimal`` a dos decimales. Nunca usa ``float``."""

    monto: Decimal
    moneda: str = "MXN"

    def __post_init__(self) -> None:
        if not isinstance(self.monto, Decimal):
            raise ImporteInvalido("el monto debe ser Decimal; use Dinero.de(...)")
        if not self.monto.is_finite() or self.monto < 0:
            raise ImporteInvalido(f"importe no válido: {self.monto}")
        object.__setattr__(self, "monto", self.monto.quantize(_CENTAVOS, ROUND_HALF_UP))

    @classmethod
    def de(cls, valor: int | str | Decimal, moneda: str = "MXN") -> Dinero:
        """Construye desde int, str o Decimal. Rechaza ``float`` para evitar errores binarios."""
        if isinstance(valor, (float, bool)):
            raise ImporteInvalido("no se admite float/bool para importes; use int, str o Decimal")
        try:
            return cls(Decimal(valor), moneda)
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ImporteInvalido(f"importe no válido: {valor!r}") from exc

    @classmethod
    def cero(cls, moneda: str = "MXN") -> Dinero:
        return cls(Decimal(0), moneda)

    def _misma_moneda(self, otro: Dinero) -> None:
        if self.moneda != otro.moneda:
            raise ImporteInvalido(f"monedas distintas: {self.moneda} y {otro.moneda}")

    def __add__(self, otro: Dinero) -> Dinero:
        self._misma_moneda(otro)
        return Dinero(self.monto + otro.monto, self.moneda)

    def por(self, cantidad: Cantidad | int) -> Dinero:
        factor = cantidad.valor if isinstance(cantidad, Cantidad) else cantidad
        if not isinstance(factor, int) or isinstance(factor, bool) or factor < 0:
            raise CantidadInvalida(f"factor no válido: {factor!r}")
        return Dinero(self.monto * factor, self.moneda)

    def porcentaje(self, pct: int | str | Decimal) -> Dinero:
        return Dinero(self.monto * Decimal(pct) / Decimal(100), self.moneda)

    def __lt__(self, otro: Dinero) -> bool:
        self._misma_moneda(otro)
        return self.monto < otro.monto

    def __str__(self) -> str:
        return f"{self.monto} {self.moneda}"


@dataclass(frozen=True)
class Cantidad:
    """Cantidad entera estrictamente positiva."""

    valor: int

    def __post_init__(self) -> None:
        if not isinstance(self.valor, int) or isinstance(self.valor, bool) or self.valor <= 0:
            raise CantidadInvalida(f"la cantidad debe ser un entero positivo: {self.valor!r}")

    def __add__(self, otra: Cantidad) -> Cantidad:
        return Cantidad(self.valor + otra.valor)
