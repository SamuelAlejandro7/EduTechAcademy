"""Dobles en memoria para probar dominio y aplicación sin base de datos.

Las implementaciones reales (CSV/SQLAlchemy) las construye el Integrante 3 en src/Infrastructure.
"""

from __future__ import annotations

from src.Application.ports import PublicadorEventos
from src.Domain.entities import Actor, Operacion, RecursoFormativo
from src.Domain.events import EventoDeDominio
from src.Domain.repositories import ActorRepository, OperacionRepository, RecursoRepository


class ActoresEnMemoria(ActorRepository):
    def __init__(self, actores: list[Actor] | None = None) -> None:
        self.datos = {a.actor_id: a for a in (actores or [])}

    def obtener(self, actor_id: str) -> Actor | None:
        return self.datos.get(actor_id)


class RecursosEnMemoria(RecursoRepository):
    def __init__(self, recursos: list[RecursoFormativo] | None = None) -> None:
        self.datos = {r.recurso_id: r for r in (recursos or [])}

    def obtener(self, recurso_id: str) -> RecursoFormativo | None:
        return self.datos.get(recurso_id)

    def guardar(self, recurso: RecursoFormativo) -> None:
        self.datos[recurso.recurso_id] = recurso


class OperacionesEnMemoria(OperacionRepository):
    def __init__(self, operaciones: list[Operacion] | None = None) -> None:
        self.datos = {o.operacion_id: o for o in (operaciones or [])}

    def obtener(self, operacion_id: str) -> Operacion | None:
        return self.datos.get(operacion_id)

    def guardar(self, operacion: Operacion) -> None:
        self.datos[operacion.operacion_id] = operacion


class PublicadorEnMemoria(PublicadorEventos):
    def __init__(self) -> None:
        self.eventos: list[EventoDeDominio] = []

    def publicar(self, evento: EventoDeDominio) -> None:
        self.eventos.append(evento)
