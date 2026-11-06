from datetime import datetime, timezone

from src.Domain.entities import Operacion, RecursoFormativo
from src.Domain.specifications import (
    ActorActivo,
    ActorPreferente,
    AnticipoMinimoCubierto,
    CapacidadDisponible,
    ContextoEvaluacion,
    OperacionAutorizada,
    OperacionConLineas,
    PromocionActiva,
    RecursosHabilitados,
    TotalMinimo,
    beneficio_referencia,
    puede_inscribirse,
    puede_procesarse,
)
from src.Domain.value_objects import Dinero

AHORA = datetime(2026, 10, 2, tzinfo=timezone.utc)


def ctx(op, actor=None, recursos=None, pago=None):
    return ContextoEvaluacion(operacion=op, actor=actor, recursos=recursos or {}, monto_pagado=pago)


def operacion_con(recurso, cantidad=1, **kw):
    op = Operacion("O", "A", AHORA, **kw)
    op.agregar_linea(recurso, cantidad)
    return op


# --- reglas simples ---------------------------------------------------------------
def test_actor_activo(actor, operacion):
    assert ActorActivo().is_satisfied_by(ctx(operacion, actor))
    actor.activo = False
    assert not ActorActivo().is_satisfied_by(ctx(operacion, actor))
    assert not ActorActivo().is_satisfied_by(ctx(operacion, None))


def test_operacion_con_lineas(operacion):
    vacia = Operacion("O2", "A1", AHORA)
    assert OperacionConLineas().is_satisfied_by(ctx(operacion))
    assert not OperacionConLineas().is_satisfied_by(ctx(vacia))


def test_operacion_autorizada(operacion):
    assert OperacionAutorizada().is_satisfied_by(ctx(operacion))
    operacion.autorizado = False
    assert not OperacionAutorizada().is_satisfied_by(ctx(operacion))


def test_actor_preferente(actor, preferente, operacion):
    assert ActorPreferente().is_satisfied_by(ctx(operacion, preferente))
    assert not ActorPreferente().is_satisfied_by(ctx(operacion, actor))
    assert not ActorPreferente().is_satisfied_by(ctx(operacion, None))


def test_total_minimo_en_el_limite(recurso):
    # 1 x 800 < 1500 ; 2 x 800 = 1600 >= 1500
    assert not TotalMinimo().is_satisfied_by(ctx(operacion_con(recurso, 1)))
    assert TotalMinimo().is_satisfied_by(ctx(operacion_con(recurso, 2)))
    exacto = RecursoFormativo("PX", "X", Dinero.de(1500), 5)
    assert TotalMinimo().is_satisfied_by(ctx(operacion_con(exacto, 1)))
    casi = RecursoFormativo("PY", "Y", Dinero.de("1499.99"), 5)
    assert not TotalMinimo().is_satisfied_by(ctx(operacion_con(casi, 1)))


def test_promocion_activa(operacion):
    assert not PromocionActiva().is_satisfied_by(ctx(operacion))
    operacion.promocion_activa = True
    assert PromocionActiva().is_satisfied_by(ctx(operacion))


def test_recursos_habilitados(operacion, recurso):
    assert RecursosHabilitados().is_satisfied_by(ctx(operacion, recursos={"P1": recurso}))
    recurso.habilitado = False
    assert not RecursosHabilitados().is_satisfied_by(ctx(operacion, recursos={"P1": recurso}))
    assert not RecursosHabilitados().is_satisfied_by(ctx(operacion, recursos={}))


def test_capacidad_disponible(operacion, recurso):
    assert CapacidadDisponible().is_satisfied_by(ctx(operacion, recursos={"P1": recurso}))
    recurso.capacidad = 0
    assert not CapacidadDisponible().is_satisfied_by(ctx(operacion, recursos={"P1": recurso}))
    assert not CapacidadDisponible().is_satisfied_by(ctx(operacion, recursos={}))


def test_anticipo_minimo_en_el_limite(recurso):
    op = operacion_con(recurso, 1)  # total 800 -> 50 % = 400
    assert not AnticipoMinimoCubierto().is_satisfied_by(ctx(op))  # sin pago informado
    assert AnticipoMinimoCubierto().is_satisfied_by(ctx(op, pago=Dinero.de(400)))
    assert not AnticipoMinimoCubierto().is_satisfied_by(ctx(op, pago=Dinero.de("399.99")))


# --- combinadores -----------------------------------------------------------------
def test_and_or_not_se_combinan_con_operadores(operacion, actor):
    c = ctx(operacion, actor)
    assert (ActorActivo() & OperacionAutorizada()).is_satisfied_by(c)
    assert not (ActorActivo() & PromocionActiva()).is_satisfied_by(c)
    assert (PromocionActiva() | ActorActivo()).is_satisfied_by(c)
    assert not (PromocionActiva() | ActorPreferente()).is_satisfied_by(c)
    assert (~PromocionActiva()).is_satisfied_by(c)
    assert not (~ActorActivo()).is_satisfied_by(c)


def test_descripcion_de_reglas_compuestas():
    regla = ActorActivo() & ~PromocionActiva()
    assert regla.descripcion == "(actor activo AND NOT(promoción activa))"
    assert (ActorActivo() | ActorPreferente()).descripcion == "(actor activo OR actor preferente)"


def test_explicar_lista_solo_lo_que_falla(operacion, actor):
    actor.activo = False
    operacion.autorizado = False
    motivos = puede_procesarse().explicar(ctx(operacion, actor))
    assert motivos == ("actor activo", "operación autorizada")


def test_explicar_not_y_or(operacion, preferente):
    operacion.promocion_activa = True
    assert (~PromocionActiva()).explicar(ctx(operacion, preferente)) == ("NOT(promoción activa)",)
    texto = (ActorPreferente() & (PromocionActiva() | OperacionAutorizada())).explicar(
        ctx(operacion, preferente)
    )
    assert texto == ()
    operacion.promocion_activa = False
    operacion.autorizado = False
    fallo = (PromocionActiva() | OperacionAutorizada()).explicar(ctx(operacion, preferente))
    assert fallo[0].startswith("ninguna de:")


# --- reglas de negocio nombradas -------------------------------------------------------
def test_puede_procesarse_caso_feliz(operacion, actor):
    assert puede_procesarse().is_satisfied_by(ctx(operacion, actor))


def test_puede_procesarse_falla_por_cada_condicion(operacion, actor):
    actor.activo = False
    assert not puede_procesarse().is_satisfied_by(ctx(operacion, actor))
    actor.activo = True
    operacion.autorizado = False
    assert not puede_procesarse().is_satisfied_by(ctx(operacion, actor))
    vacia = Operacion("O2", "A1", AHORA, autorizado=True)
    assert not puede_procesarse().is_satisfied_by(ctx(vacia, actor))


def test_beneficio_referencia(preferente, actor, recurso):
    grande = operacion_con(recurso, 2)  # 1600
    assert beneficio_referencia().is_satisfied_by(ctx(grande, preferente))
    assert not beneficio_referencia().is_satisfied_by(ctx(grande, actor))  # no preferente
    grande.promocion_activa = True
    assert not beneficio_referencia().is_satisfied_by(ctx(grande, preferente))  # NOT promoción
    chica = operacion_con(recurso, 1)  # 800 < 1500
    assert not beneficio_referencia().is_satisfied_by(ctx(chica, preferente))


def test_puede_inscribirse_con_y_sin_anticipo(operacion, recurso):
    recursos = {"P1": recurso}
    assert puede_inscribirse().is_satisfied_by(ctx(operacion, recursos=recursos))
    exigente = puede_inscribirse(exigir_anticipo=True)
    assert not exigente.is_satisfied_by(ctx(operacion, recursos=recursos))
    assert exigente.is_satisfied_by(ctx(operacion, recursos=recursos, pago=Dinero.de(400)))
