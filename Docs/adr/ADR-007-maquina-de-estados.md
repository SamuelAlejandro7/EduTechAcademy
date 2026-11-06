# ADR-007: Máquina de estados dirigida por tabla

* **Estado:** Aceptada
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
El flujo de referencia es SOLICITADA → ACEPTADA → INSCRITA → FINALIZADA, con la alternativa
SOLICITADA → CANCELADA. Toda otra transición debe bloquearse, y el paquete incluye pruebas de
transiciones inválidas (repetir aprobación, saltar estados).

## Decisión
Las transiciones válidas se declaran en un diccionario `(estado, acción) → estado destino`
(`TRANSICIONES` en `src/Domain/state_machine.py`). La función `siguiente_estado` consulta la
tabla y lanza `TransicionInvalida` si el par no existe, indicando las acciones permitidas.
`Operacion` consulta la máquina **antes** de evaluar reglas o registrar eventos, así que una
transición inválida nunca deja la operación a medias.

| Estado | Acción | Destino | Precondición | Evento |
|---|---|---|---|---|
| SOLICITADA | aceptar | ACEPTADA | `puede_procesarse` | `OperacionAceptada` (+ `BeneficioReferenciaOtorgado`) |
| ACEPTADA | inscribir | INSCRITA | `puede_inscribirse` | `OperacionInscrita` |
| INSCRITA | finalizar | FINALIZADA | — | `OperacionFinalizada` |
| SOLICITADA | cancelar | CANCELADA | — | `OperacionCancelada` |

## Alternativas consideradas
1. **Patrón State con una clase por estado.** Descartada: para cinco estados y cuatro acciones
   agrega mucho código sin más claridad que una tabla.
2. **`if estado == ...` repartidos en cada método.** Descartada: es fácil olvidar un caso y no
   hay un único lugar donde ver el flujo.

## Consecuencias
* (+) El flujo completo se lee en seis líneas y se prueba recorriendo todas las combinaciones
  estado × acción (`test_toda_combinacion_fuera_de_la_tabla_es_invalida`).
* (+) Permitir, por ejemplo, cancelar desde ACEPTADA es agregar una fila.
* (−) Las precondiciones por transición no están en la tabla; las aplica `Operacion` en cada
  método. Se acepta porque dependen de datos distintos en cada paso.
