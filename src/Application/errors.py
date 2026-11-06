"""Errores propios de la capa de aplicación."""

from __future__ import annotations

from src.Domain.errors import ErrorDeDominio


class EntidadNoEncontrada(ErrorDeDominio):
    """El actor, recurso u operación solicitado no existe (sugerido: HTTP 404)."""

    codigo = "ENTIDAD_NO_ENCONTRADA"
