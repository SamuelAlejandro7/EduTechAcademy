"""Puertos de salida de la aplicación."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.Domain.events import EventoDeDominio


class PublicadorEventos(ABC):
    """Publica los Domain Events (bus en memoria, cola, log...). Lo implementa infraestructura."""

    @abstractmethod
    def publicar(self, evento: EventoDeDominio) -> None: ...
