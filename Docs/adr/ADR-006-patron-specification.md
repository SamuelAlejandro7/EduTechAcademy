# ADR-006: Reglas de negocio con el patrón Specification (AND / OR / NOT)

* **Estado:** Aceptada
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
El PIA exige al menos tres Specifications combinables con AND, OR y NOT. Las reglas del paquete
(`puede_procesarse`, `beneficio_referencia`) son conjunciones de condiciones simples, y se
necesita saber **por qué** una operación falla, no solo que falla.

## Decisión
* Se define la clase abstracta `Specification` con `is_satisfied_by(ctx)` y `explicar(ctx)`.
* Los combinadores `And`, `Or` y `Not` se exponen con los operadores `&`, `|` y `~`.
* Cada condición simple es una clase con una sola responsabilidad (nueve en total).
* Las reglas de negocio son funciones que arman las combinaciones:
  `puede_procesarse() = ActorActivo & OperacionConLineas & OperacionAutorizada` y
  `beneficio_referencia() = ActorPreferente & TotalMinimo(1500) & ~PromocionActiva`.
* Las reglas se evalúan sobre un `ContextoEvaluacion` (operación, actor, recursos, monto pagado).
* `explicar()` devuelve únicamente las condiciones hoja que no se cumplen, para construir
  mensajes de error y la evidencia de cada caso de prueba.

## Alternativas consideradas
1. **`if` anidados dentro de `Operacion`.** Descartada: no se reutilizan, no se prueban por
   separado y no permiten explicar cuál condición falló.
2. **Una función booleana por regla.** Descartada: no se pueden componer con NOT/OR sin
   reescribirlas.

## Consecuencias
* (+) Cada regla simple tiene su propia prueba (límites de 1500, 50 %, etc.).
* (+) Agregar una regla nueva es agregar una clase y combinarla; no se modifica código existente.
* (+) Los motivos de rechazo viajan en el error (`motivos`) y aparecen en la evidencia.
* (−) Más clases que un `if`, a cambio de reutilización y trazabilidad.
