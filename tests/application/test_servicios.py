from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.Application.dto import (
    AplicarAccionCommand,
    LineaSolicitada,
    SolicitarOperacionCommand,
)
from src.Application.errors import EntidadNoEncontrada
from src.Application.services import ACCIONES_PIA, ServicioOperaciones
from src.Domain.entities import Actor, Operacion, RecursoFormativo
from src.Domain.errors import (
    CantidadInvalida,
    CapacidadInsuficiente,
    ErrorDeDominio,
    ErrorDeEstado,
    ErrorDeValidacion,
    InscripcionNoPermitida,
    OperacionNoProcesable,
    RecursoNoHabilitado,
    TransicionInvalida,
)
from src.Domain.state_machine import Accion
from src.Domain.value_objects import Dinero
from tests.fakes import (
    ActoresEnMemoria,
    OperacionesEnMemoria,
    PublicadorEnMemoria,
    RecursosEnMemoria,
)

AHORA = datetime(2026, 10, 2, tzinfo=timezone.utc)


@pytest.fixture
def mundo():
    actores = ActoresEnMemoria(
        [
            Actor("A1", "Alumno 1", False, True, "Monterrey"),
            Actor("A2", "Alumno 2", True, True, "Monterrey"),
            Actor("A3", "Alumno 3", False, False, "Apodaca"),
        ]
    )
    recursos = RecursosEnMemoria(
        [
            RecursoFormativo("P1", "Cloud 01", Dinero.de(800), 10, True),
            RecursoFormativo("P2", "Data 02", Dinero.de(1000), 5, True),
            RecursoFormativo("P3", "Cerrado 03", Dinero.de(500), 5, False),
        ]
    )
    operaciones = OperacionesEnMemoria()
    publicador = PublicadorEnMemoria()
    servicio = ServicioOperaciones(actores, recursos, operaciones, publicador)
    return servicio, recursos, operaciones, publicador


def solicitar(servicio, op_id="O1", actor="A1", lineas=(("P1", 2),), **kw):
    cmd = SolicitarOperacionCommand(
        op_id,
        actor,
        tuple(LineaSolicitada(r, c) for r, c in lineas),
        referencia="REF",
        autorizado=kw.pop("autorizado", True),
        fecha_solicitud=AHORA,
        **kw,
    )
    return servicio.solicitar_operacion(cmd)


# --- solicitar --------------------------------------------------------------------
def test_solicitar_operacion_calcula_total_con_decimal(mundo):
    servicio, *_ = mundo
    dto = solicitar(servicio, lineas=(("P1", 2), ("P2", 1)))
    assert dto.estado == "SOLICITADA"
    assert dto.total == Decimal("2600.00")
    assert [l.subtotal for l in dto.lineas] == [Decimal("1600.00"), Decimal("1000.00")]


def test_solicitar_valida_cantidad(mundo):
    servicio, *_ = mundo
    with pytest.raises(CantidadInvalida):
        solicitar(servicio, lineas=(("P1", 0),))


def test_solicitar_valida_habilitacion_y_cupo(mundo):
    servicio, *_ = mundo
    with pytest.raises(RecursoNoHabilitado):
        solicitar(servicio, lineas=(("P3", 1),))
    with pytest.raises(CapacidadInsuficiente):
        solicitar(servicio, lineas=(("P2", 6),))


def test_solicitar_con_actor_o_recurso_inexistente(mundo):
    servicio, *_ = mundo
    with pytest.raises(EntidadNoEncontrada, match="actor"):
        solicitar(servicio, actor="NOEXISTE")
    with pytest.raises(EntidadNoEncontrada, match="recurso"):
        solicitar(servicio, lineas=(("NOEXISTE", 1),))


def test_obtener_operacion_y_no_encontrada(mundo):
    servicio, *_ = mundo
    solicitar(servicio)
    assert servicio.obtener_operacion("O1").operacion_id == "O1"
    with pytest.raises(EntidadNoEncontrada):
        servicio.obtener_operacion("XX")


# --- reglas -------------------------------------------------------------------------
def test_validar_operacion_cumple(mundo):
    servicio, *_ = mundo
    solicitar(servicio)
    r = servicio.validar_operacion("O1")
    assert r.cumple and r.motivos_incumplidos == () and r.regla == "puede_procesarse"


def test_validar_operacion_reporta_motivos(mundo):
    servicio, *_ = mundo
    solicitar(servicio, actor="A3", autorizado=False)
    r = servicio.validar_operacion("O1")
    assert not r.cumple
    assert r.motivos_incumplidos == ("actor activo", "operación autorizada")


def test_validar_operacion_con_actor_inexistente_en_repositorio(mundo):
    servicio, _, operaciones, _ = mundo
    operaciones.guardar(Operacion("OX", "FANTASMA", AHORA, autorizado=True))
    r = servicio.validar_operacion("OX")
    assert not r.cumple
    assert "actor activo" in r.motivos_incumplidos
    assert "operación con al menos una línea" in r.motivos_incumplidos


def test_evaluar_beneficio(mundo):
    servicio, *_ = mundo
    solicitar(servicio, "O1", actor="A2", lineas=(("P1", 2),))  # preferente, 1600
    solicitar(servicio, "O2", actor="A2", lineas=(("P1", 1),))  # 800
    solicitar(servicio, "O3", actor="A2", lineas=(("P1", 2),), promocion_activa=True)
    assert servicio.evaluar_beneficio("O1").cumple
    assert servicio.evaluar_beneficio("O2").motivos_incumplidos == ("total >= 1500.00 MXN",)
    assert servicio.evaluar_beneficio("O3").motivos_incumplidos == ("NOT(promoción activa)",)


# --- acciones ------------------------------------------------------------------------
def test_aplicar_accion_aceptar_publica_eventos(mundo):
    servicio, _, _, publicador = mundo
    solicitar(servicio, actor="A2", lineas=(("P1", 2),))
    r = servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.ACEPTAR))
    assert (r.estado_inicial, r.estado_final) == ("SOLICITADA", "ACEPTADA")
    assert r.eventos == ("OperacionAceptada", "BeneficioReferenciaOtorgado")
    assert [e.nombre for e in publicador.eventos] == list(r.eventos)


def test_inscribir_persiste_el_cupo_reservado(mundo):
    servicio, recursos, _, _ = mundo
    solicitar(servicio)
    servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.ACEPTAR))
    servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.INSCRIBIR))
    assert recursos.obtener("P1").capacidad == 8


def test_inscribir_con_anticipo(mundo):
    servicio, *_ = mundo
    solicitar(servicio)  # total 1600 -> anticipo mínimo 800
    servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.ACEPTAR))
    with pytest.raises(InscripcionNoPermitida):
        servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.INSCRIBIR, Decimal("799.99")))
    r = servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.INSCRIBIR, Decimal(800)))
    assert r.estado_final == "INSCRITA"


def test_finalizar_y_cancelar(mundo):
    servicio, *_ = mundo
    solicitar(servicio, "O1")
    solicitar(servicio, "O2")
    servicio.aplicar_accion(AplicarAccionCommand("O2", Accion.CANCELAR, motivo="cambio de planes"))
    assert servicio.obtener_operacion("O2").estado == "CANCELADA"
    solicitar(servicio, "O3")
    servicio.aplicar_accion(AplicarAccionCommand("O3", Accion.CANCELAR))
    for paso in (Accion.ACEPTAR, Accion.INSCRIBIR, Accion.FINALIZAR):
        servicio.aplicar_accion(AplicarAccionCommand("O1", paso))
    assert servicio.obtener_operacion("O1").estado == "FINALIZADA"


def test_aplicar_accion_sobre_operacion_inexistente(mundo):
    servicio, *_ = mundo
    with pytest.raises(EntidadNoEncontrada):
        servicio.aplicar_accion(AplicarAccionCommand("XX", Accion.ACEPTAR))


def test_actor_de_operacion_desaparecido_da_no_encontrado(mundo):
    servicio, _, operaciones, _ = mundo
    operaciones.guardar(Operacion("OX", "FANTASMA", AHORA, autorizado=True))
    with pytest.raises(EntidadNoEncontrada):
        servicio.aplicar_accion(AplicarAccionCommand("OX", Accion.ACEPTAR))


def test_inscribir_con_recurso_que_ya_no_existe(mundo):
    servicio, recursos, _operaciones, _ = mundo
    solicitar(servicio)
    servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.ACEPTAR))
    del recursos.datos["P1"]
    with pytest.raises(InscripcionNoPermitida):
        servicio.aplicar_accion(AplicarAccionCommand("O1", Accion.INSCRIBIR))


# --- acciones del paquete de pruebas ---------------------------------------------------
@pytest.mark.parametrize(
    ("accion", "final", "primer_evento"),
    [
        ("aprobar", "ACEPTADA", "OperacionAceptada"),
        ("completar", "FINALIZADA", "OperacionAceptada"),
        ("cancelar", "CANCELADA", "OperacionCancelada"),
    ],
)
def test_acciones_pia_exitosas(mundo, accion, final, primer_evento):
    servicio, *_ = mundo
    solicitar(servicio)
    r = servicio.ejecutar_accion_pia("O1", accion)
    assert r.estado_inicial == "SOLICITADA" and r.estado_final == final
    assert r.eventos[0] == primer_evento


def test_repetir_aprobacion_falla_en_el_segundo_paso_y_conserva_el_primero(mundo):
    servicio, *_ = mundo
    solicitar(servicio)
    with pytest.raises(TransicionInvalida):
        servicio.ejecutar_accion_pia("O1", "repetir_aprobacion")
    assert servicio.obtener_operacion("O1").estado == "ACEPTADA"


def test_saltar_estado_es_invalido_y_no_cambia_el_estado(mundo):
    servicio, *_ = mundo
    solicitar(servicio)
    with pytest.raises(TransicionInvalida):
        servicio.ejecutar_accion_pia("O1", "saltar_estado")
    assert servicio.obtener_operacion("O1").estado == "SOLICITADA"


def test_accion_pia_sobre_operacion_no_procesable(mundo):
    servicio, *_ = mundo
    solicitar(servicio, actor="A3")
    with pytest.raises(OperacionNoProcesable):
        servicio.ejecutar_accion_pia("O1", "aprobar")


def test_accion_pia_desconocida(mundo):
    servicio, *_ = mundo
    solicitar(servicio)
    with pytest.raises(ErrorDeDominio, match="desconocida"):
        servicio.ejecutar_accion_pia("O1", "volar")


def test_todas_las_acciones_del_csv_estan_mapeadas():
    assert set(ACCIONES_PIA) == {
        "aprobar",
        "completar",
        "cancelar",
        "repetir_aprobacion",
        "saltar_estado",
    }


def test_taxonomia_de_errores_para_la_api():
    assert issubclass(TransicionInvalida, ErrorDeEstado)
    assert issubclass(CapacidadInsuficiente, ErrorDeEstado)
    assert issubclass(OperacionNoProcesable, ErrorDeValidacion)
    assert issubclass(EntidadNoEncontrada, ErrorDeDominio)
    assert TransicionInvalida.codigo == "TRANSICION_INVALIDA"
