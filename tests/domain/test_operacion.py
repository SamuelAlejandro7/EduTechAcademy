from datetime import datetime

import pytest

from src.Domain import events as ev
from src.Domain.entities import Operacion, RecursoFormativo
from src.Domain.errors import (
    CantidadInvalida,
    CapacidadInsuficiente,
    InscripcionNoPermitida,
    OperacionNoModificable,
    OperacionNoProcesable,
    RecursoNoHabilitado,
    TransicionInvalida,
)
from src.Domain.value_objects import Cantidad, Dinero
from src.Domain.value_objects import EstadoOperacion as E
from tests.domain.conftest import AHORA


# --- Recurso ----------------------------------------------------------------------
def test_recurso_reserva_descuenta_cupo(recurso):
    recurso.reservar(Cantidad(4))
    assert recurso.capacidad == 6


def test_recurso_reserva_exacta_agota_cupo(recurso):
    recurso.reservar(Cantidad(10))
    assert recurso.capacidad == 0
    assert not recurso.tiene_cupo(Cantidad(1))


def test_recurso_sin_cupo_suficiente(recurso):
    with pytest.raises(CapacidadInsuficiente, match="solicitado 11, disponible 10"):
        recurso.reservar(Cantidad(11))


def test_recurso_deshabilitado_no_reserva(recurso):
    recurso.habilitado = False
    with pytest.raises(RecursoNoHabilitado):
        recurso.reservar(Cantidad(1))


def test_recurso_capacidad_negativa_es_invalida():
    with pytest.raises(CantidadInvalida):
        RecursoFormativo("P", "X", Dinero.de(1), capacidad=-1)


# --- Líneas y total -----------------------------------------------------------------
def test_total_es_suma_de_precio_por_cantidad(recurso, recurso_caro):
    op = Operacion("O", "A", AHORA)
    op.agregar_linea(recurso, 3)  # 2400
    op.agregar_linea(recurso_caro, 2)  # 2000
    assert op.total() == Dinero.de(4400)


def test_operacion_vacia_tiene_total_cero():
    assert Operacion("O", "A", AHORA).total() == Dinero.cero()


def test_agregar_la_misma_linea_suma_cantidades(recurso):
    op = Operacion("O", "A", AHORA)
    op.agregar_linea(recurso, 2)
    op.agregar_linea(recurso, 3)
    assert len(op.lineas) == 1
    assert op.lineas[0].cantidad == Cantidad(5)


@pytest.mark.parametrize("cantidad", [0, -1, 2.5])
def test_agregar_linea_rechaza_cantidades_invalidas(recurso, cantidad):
    with pytest.raises(CantidadInvalida):
        Operacion("O", "A", AHORA).agregar_linea(recurso, cantidad)


def test_agregar_linea_rechaza_recurso_deshabilitado(recurso):
    recurso.habilitado = False
    with pytest.raises(RecursoNoHabilitado):
        Operacion("O", "A", AHORA).agregar_linea(recurso, 1)


def test_agregar_linea_respeta_la_capacidad(recurso):
    op = Operacion("O", "A", AHORA)
    op.agregar_linea(recurso, 10)  # límite exacto: permitido
    with pytest.raises(CapacidadInsuficiente):
        op.agregar_linea(recurso, 1)  # acumulado 11 > 10


def test_no_se_editan_lineas_fuera_de_solicitada(operacion, actor, recurso):
    operacion.aceptar(actor)
    with pytest.raises(OperacionNoModificable):
        operacion.agregar_linea(recurso, 1)


# --- Transiciones --------------------------------------------------------------------
def test_ciclo_completo_y_eventos(operacion, actor, recurso):
    operacion.aceptar(actor, AHORA)
    operacion.inscribir({"P1": recurso}, ahora=AHORA)
    operacion.finalizar(AHORA)
    assert operacion.estado is E.FINALIZADA
    nombres = [e.nombre for e in operacion.pull_events()]
    assert nombres == ["OperacionAceptada", "OperacionInscrita", "OperacionFinalizada"]
    assert operacion.pull_events() == []  # se limpian al entregarlos


def test_aceptar_exige_puede_procesarse(operacion, actor):
    actor.activo = False
    operacion.autorizado = False
    with pytest.raises(OperacionNoProcesable) as exc:
        operacion.aceptar(actor)
    assert exc.value.motivos == ("actor activo", "operación autorizada")
    assert operacion.estado is E.SOLICITADA  # no cambió
    assert operacion.pull_events() == []


def test_aceptar_dos_veces_es_transicion_invalida(operacion, actor):
    operacion.aceptar(actor)
    with pytest.raises(TransicionInvalida):
        operacion.aceptar(actor)


def test_aceptar_emite_beneficio_para_preferente_con_total_alto(preferente, recurso):
    op = Operacion("O", "A2", AHORA, autorizado=True)
    op.agregar_linea(recurso, 2)  # 1600
    op.aceptar(preferente, AHORA)
    eventos = op.pull_events()
    assert [e.nombre for e in eventos] == ["OperacionAceptada", "BeneficioReferenciaOtorgado"]
    assert isinstance(eventos[1], ev.BeneficioReferenciaOtorgado)
    assert eventos[1].total == Dinero.de(1600)


def test_aceptar_no_emite_beneficio_con_promocion(preferente, recurso):
    op = Operacion("O", "A2", AHORA, autorizado=True, promocion_activa=True)
    op.agregar_linea(recurso, 2)
    op.aceptar(preferente)
    assert [e.nombre for e in op.pull_events()] == ["OperacionAceptada"]


def test_inscribir_reserva_cupo(operacion, actor, recurso):
    operacion.aceptar(actor)
    operacion.inscribir({"P1": recurso})
    assert recurso.capacidad == 9


def test_inscribir_con_anticipo_en_el_limite(operacion, actor, recurso):
    operacion.aceptar(actor)
    operacion.inscribir({"P1": recurso}, monto_pagado=Dinero.de(400))  # 50 % de 800
    assert operacion.estado is E.INSCRITA


def test_inscribir_con_anticipo_insuficiente(operacion, actor, recurso):
    operacion.aceptar(actor)
    with pytest.raises(InscripcionNoPermitida, match="anticipo"):
        operacion.inscribir({"P1": recurso}, monto_pagado=Dinero.de("399.99"))
    assert operacion.estado is E.ACEPTADA
    assert recurso.capacidad == 10  # no se reservó nada


def test_inscribir_con_recurso_deshabilitado(operacion, actor, recurso):
    operacion.aceptar(actor)
    recurso.habilitado = False
    with pytest.raises(InscripcionNoPermitida, match="habilitados"):
        operacion.inscribir({"P1": recurso})


def test_inscribir_sin_cupo(operacion, actor, recurso):
    operacion.aceptar(actor)
    recurso.capacidad = 0
    with pytest.raises(InscripcionNoPermitida, match="cupo"):
        operacion.inscribir({"P1": recurso})


def test_saltar_estados_es_invalido(operacion, actor, recurso):
    with pytest.raises(TransicionInvalida):
        operacion.inscribir({"P1": recurso})  # SOLICITADA -> INSCRITA
    with pytest.raises(TransicionInvalida):
        operacion.finalizar()  # SOLICITADA -> FINALIZADA


def test_cancelar_desde_solicitada(operacion):
    operacion.cancelar("ya no lo necesito", AHORA)
    assert operacion.estado is E.CANCELADA
    evento = operacion.pull_events()[0]
    assert isinstance(evento, ev.OperacionCancelada)
    assert evento.motivo == "ya no lo necesito"


def test_cancelar_con_motivo_por_defecto(operacion):
    operacion.cancelar()
    assert operacion.pull_events()[0].motivo == "cancelada por el solicitante"


def test_estados_finales_son_inmutables(operacion, actor, recurso):
    operacion.cancelar()
    for accion in (lambda: operacion.aceptar(actor), operacion.finalizar, operacion.cancelar):
        with pytest.raises(TransicionInvalida):
            accion()


def test_no_se_cancela_una_operacion_aceptada(operacion, actor):
    operacion.aceptar(actor)
    with pytest.raises(TransicionInvalida):
        operacion.cancelar()


def test_evento_usa_hora_actual_si_no_se_indica(operacion):
    operacion.cancelar()
    assert isinstance(operacion.pull_events()[0].ocurrido_en, datetime)
