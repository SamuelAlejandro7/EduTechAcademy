"""Errores del dominio de EduTech Academy.

Se agrupan en dos familias para que la capa de API (Integrante 3) pueda
traducirlos a códigos HTTP sin conocer el detalle de cada regla:

* ``ErrorDeValidacion``  -> la petición viola una regla de negocio (sugerido: 422).
* ``ErrorDeEstado``      -> la petición choca con el estado actual (sugerido: 409).

La capa de aplicación agrega ``EntidadNoEncontrada`` (sugerido: 404).
"""

from __future__ import annotations


class ErrorDeDominio(Exception):
    """Base de todos los errores de negocio. Lleva un código estable y los motivos."""

    codigo = "ERROR_DE_DOMINIO"

    def __init__(self, mensaje: str, motivos: tuple[str, ...] = ()) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.motivos = tuple(motivos)

    def __str__(self) -> str:
        if self.motivos:
            return f"{self.mensaje}: {'; '.join(self.motivos)}"
        return self.mensaje


class ErrorDeValidacion(ErrorDeDominio):
    codigo = "ERROR_DE_VALIDACION"


class ErrorDeEstado(ErrorDeDominio):
    codigo = "ERROR_DE_ESTADO"


# --- Validación -------------------------------------------------------------
class CantidadInvalida(ErrorDeValidacion):
    codigo = "CANTIDAD_INVALIDA"


class ImporteInvalido(ErrorDeValidacion):
    codigo = "IMPORTE_INVALIDO"


class RecursoNoHabilitado(ErrorDeValidacion):
    codigo = "RECURSO_NO_HABILITADO"


class OperacionNoProcesable(ErrorDeValidacion):
    """No se cumple ``puede_procesarse`` (actor activo, con líneas y autorizada)."""

    codigo = "OPERACION_NO_PROCESABLE"


class InscripcionNoPermitida(ErrorDeValidacion):
    """No se cumplen las precondiciones para inscribir (recursos, cupo, anticipo)."""

    codigo = "INSCRIPCION_NO_PERMITIDA"


# --- Estado -----------------------------------------------------------------
class TransicionInvalida(ErrorDeEstado):
    codigo = "TRANSICION_INVALIDA"


class CapacidadInsuficiente(ErrorDeEstado):
    codigo = "CAPACIDAD_INSUFICIENTE"


class OperacionNoModificable(ErrorDeEstado):
    codigo = "OPERACION_NO_MODIFICABLE"
