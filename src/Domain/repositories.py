"""Puertos de persistencia (interfaces). Las implementaciones viven en src/Infrastructure."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.Domain.entities import Actor, Operacion, RecursoFormativo


class ActorRepository(ABC):
    @abstractmethod
    def obtener(self, actor_id: str) -> Actor | None: ...


class RecursoRepository(ABC):
    @abstractmethod
    def obtener(self, recurso_id: str) -> RecursoFormativo | None: ...

    @abstractmethod
    def guardar(self, recurso: RecursoFormativo) -> None: ...


class OperacionRepository(ABC):
    @abstractmethod
    def obtener(self, operacion_id: str) -> Operacion | None: ...

    @abstractmethod
    def guardar(self, operacion: Operacion) -> None: ...
