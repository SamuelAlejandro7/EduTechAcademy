# ADR-005: `Operacion` como raíz de agregado; referencias por identificador

* **Estado:** Aceptada
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
Los datos del paquete relacionan operaciones con actores, recursos y líneas de detalle. Hay que
decidir qué objetos se modifican juntos y dónde se protegen las reglas de consistencia.

## Decisión
* `Operacion` es la **raíz del agregado** y contiene sus `LineaOperacion`. Las líneas solo se
  crean y modifican a través de la raíz (`agregar_linea`), nunca de forma independiente.
* `Actor` y `RecursoFormativo` son **agregados separados**. La operación los referencia solo por
  identificador (`actor_id`, `recurso_id`), no por objeto.
* La línea guarda un **snapshot del precio** (`precio_unitario`) vigente al solicitar, de modo que
  un cambio posterior de precio en el catálogo no altere operaciones ya hechas.
* Las reglas que necesitan datos de otros agregados (el actor, los recursos) reciben esos datos
  como argumento (`aceptar(actor)`, `inscribir(recursos)`), en lugar de que la operación los cargue.

## Alternativas consideradas
1. **Un solo agregado grande con actor y recursos adentro.** Descartada: bloquearía el catálogo
   cada vez que se modifica una operación y mezclaría ciclos de vida distintos.
2. **Líneas como agregado propio.** Descartada: una línea no tiene sentido sin su operación y el
   total depende de todas ellas.

## Consecuencias
* (+) El total y las líneas siempre son consistentes dentro de la misma raíz.
* (+) La reserva de cupo en `inscribir` se hace sobre los recursos recibidos y se persiste después
  desde la capa de aplicación.
* (−) La capa de aplicación debe cargar actor y recursos antes de llamar a la operación. Se
  resuelve en `ServicioOperaciones`.
* (−) Reservar cupo modifica un agregado (`RecursoFormativo`) desde un método de otro. Se acepta
  porque ambos se guardan en el mismo caso de uso; si más adelante hubiera concurrencia real,
  habría que usar bloqueo optimista en el repositorio.
