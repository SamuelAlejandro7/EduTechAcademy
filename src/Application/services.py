"""Casos de uso de EduTech Academy.

La capa de aplicación solo orquesta: carga agregados, llama al dominio, persiste y publica
eventos. Las reglas viven en ``src/Domain``.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.Application.dto import (
    AplicarAccionCommand,
    OperacionDTO,
    ResultadoRegla,
    ResultadoTransicion,
    SolicitarOperacionCommand,
)
from src.Application.errors import EntidadNoEncontrada
from src.Application.ports import PublicadorEventos
from src.Domain.entities import Actor, Operacion, RecursoFormativo
from src.Domain.errors import ErrorDeDominio
from src.Domain.repositories import ActorRepository, OperacionRepository, RecursoRepository
from src.Domain.specifications import ContextoEvaluacion, beneficio_referencia, puede_procesarse
from src.Domain.state_machine import Accion
from src.Domain.value_objects import Dinero

# Acciones del paquete de pruebas (transiciones_prueba.csv) y la secuencia de pasos que representan.
ACCIONES_PIA: dict[str, tuple[Accion, ...]] = {
    "aprobar": (Accion.ACEPTAR,),
    "completar": (Accion.ACEPTAR, Accion.INSCRIBIR, Accion.FINALIZAR),
    "cancelar": (Accion.CANCELAR,),
    "repetir_aprobacion": (Accion.ACEPTAR, Accion.ACEPTAR),
    "saltar_estado": (Accion.FINALIZAR,),  # intenta saltar de SOLICITADA a FINALIZADA
}


class ServicioOperaciones:
    def __init__(
        self,
        actores: ActorRepository,
        recursos: RecursoRepository,
        operaciones: OperacionRepository,
        publicador: PublicadorEventos,
    ) -> None:
        self._actores = actores
        self._recursos = recursos
        self._operaciones = operaciones
        self._publicador = publicador

    # -- Auxiliares de carga ---------------------------------------------------
    def _operacion(self, operacion_id: str) -> Operacion:
        op = self._operaciones.obtener(operacion_id)
        if op is None:
            raise EntidadNoEncontrada(f"operación {operacion_id} no encontrada")
        return op

    def _actor(self, actor_id: str) -> Actor:
        actor = self._actores.obtener(actor_id)
        if actor is None:
            raise EntidadNoEncontrada(f"actor {actor_id} no encontrado")
        return actor

    def _recurso(self, recurso_id: str) -> RecursoFormativo:
        recurso = self._recursos.obtener(recurso_id)
        if recurso is None:
            raise EntidadNoEncontrada(f"recurso {recurso_id} no encontrado")
        return recurso

    def _recursos_de(self, op: Operacion) -> dict[str, RecursoFormativo]:
        """Recursos de la operación; los inexistentes simplemente no aparecen (la regla los rechaza)."""
        cargados = {}
        for linea in op.lineas:
            recurso = self._recursos.obtener(linea.recurso_id)
            if recurso is not None:
                cargados[linea.recurso_id] = recurso
        return cargados

    # -- Consultas -------------------------------------------------------------
    def obtener_operacion(self, operacion_id: str) -> OperacionDTO:
        return OperacionDTO.desde_dominio(self._operacion(operacion_id))

    def validar_operacion(self, operacion_id: str) -> ResultadoRegla:
        """Evalúa ``puede_procesarse`` (actor activo AND con líneas AND autorizada)."""
        op = self._operacion(operacion_id)
        ctx = ContextoEvaluacion(operacion=op, actor=self._actores.obtener(op.actor_id))
        regla = puede_procesarse()
        return ResultadoRegla(
            op.operacion_id,
            "puede_procesarse",
            regla.is_satisfied_by(ctx),
            op.total().monto,
            regla.explicar(ctx),
        )

    def evaluar_beneficio(self, operacion_id: str) -> ResultadoRegla:
        """Evalúa ``beneficio_referencia`` (preferente AND total >= 1500 AND NOT promoción)."""
        op = self._operacion(operacion_id)
        ctx = ContextoEvaluacion(operacion=op, actor=self._actores.obtener(op.actor_id))
        regla = beneficio_referencia()
        return ResultadoRegla(
            op.operacion_id,
            "beneficio_referencia",
            regla.is_satisfied_by(ctx),
            op.total().monto,
            regla.explicar(ctx),
        )

    # -- Comandos --------------------------------------------------------------
    def solicitar_operacion(self, cmd: SolicitarOperacionCommand) -> OperacionDTO:
        """Crea una operación en SOLICITADA validando cantidades, habilitación y cupo."""
        self._actor(cmd.actor_id)
        op = Operacion(
            cmd.operacion_id,
            cmd.actor_id,
            cmd.fecha_solicitud or datetime.now(timezone.utc),
            promocion_activa=cmd.promocion_activa,
            autorizado=cmd.autorizado,
            referencia=cmd.referencia,
        )
        for pedido in cmd.lineas:
            op.agregar_linea(self._recurso(pedido.recurso_id), pedido.cantidad)
        self._operaciones.guardar(op)
        return OperacionDTO.desde_dominio(op)

    def aplicar_accion(self, cmd: AplicarAccionCommand) -> ResultadoTransicion:
        """Ejecuta UNA acción de la máquina de estados sobre una operación."""
        op = self._operacion(cmd.operacion_id)
        estado_inicial = op.estado.value
        if cmd.accion is Accion.ACEPTAR:
            op.aceptar(self._actor(op.actor_id))
        elif cmd.accion is Accion.INSCRIBIR:
            recursos = self._recursos_de(op)
            monto = Dinero.de(cmd.monto_pagado) if cmd.monto_pagado is not None else None
            op.inscribir(recursos, monto)
            for recurso in recursos.values():
                self._recursos.guardar(recurso)
        elif cmd.accion is Accion.FINALIZAR:
            op.finalizar()
        else:
            if cmd.motivo:
                op.cancelar(cmd.motivo)
            else:
                op.cancelar()
        self._operaciones.guardar(op)
        eventos = op.pull_events()
        for evento in eventos:
            self._publicador.publicar(evento)
        return ResultadoTransicion(
            op.operacion_id, estado_inicial, op.estado.value, tuple(e.nombre for e in eventos)
        )

    def ejecutar_accion_pia(self, operacion_id: str, nombre_accion: str) -> ResultadoTransicion:
        """Ejecuta una acción del paquete de pruebas (aprobar, completar, cancelar,
        repetir_aprobacion, saltar_estado). Cada paso se persiste por separado, como si fueran
        peticiones distintas; si un paso falla, los anteriores permanecen y se propaga el error."""
        pasos = ACCIONES_PIA.get(nombre_accion)
        if pasos is None:
            raise ErrorDeDominio(f"acción desconocida: {nombre_accion}")
        estado_inicial = self._operacion(operacion_id).estado.value
        eventos: list[str] = []
        for accion in pasos:
            eventos += self.aplicar_accion(AplicarAccionCommand(operacion_id, accion)).eventos
        final = self._operacion(operacion_id).estado.value
        return ResultadoTransicion(operacion_id, estado_inicial, final, tuple(eventos))
