# ADR-011: Diferencias entre el modelo de pruebas del paquete y el BRD de EduTech

* **Estado:** Aceptada
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
Las instrucciones del paquete advierten que sus reglas, estados e importes son un **modelo de
pruebas propuesto**, y que el PIA debe derivarse del BRD, las historias de usuario, el BPMN y el
diseño del equipo. Si difieren, hay que documentar las diferencias y no reemplazar los
requerimientos propios.

## Decisión
Se implementan las reglas del paquete (para poder ejecutar los 120 casos y las 20 transiciones),
junto con **una regla del BRD** (anticipo mínimo del 50 %), y se documentan las diferencias.

| Tema | Modelo del paquete | BRD / historias de EduTech | Tratamiento |
|---|---|---|---|
| Estados | SOLICITADA → ACEPTADA → INSCRITA → FINALIZADA / CANCELADA | Preinscripción pendiente de pago → inscrito → curso cerrado; certificación al final | Equivalencia propuesta: SOLICITADA ≈ preinscripción, INSCRITA ≈ inscripción confirmada, FINALIZADA ≈ curso cerrado. ACEPTADA es un paso intermedio del modelo que el BRD no nombra. |
| Beneficio | `beneficio_referencia` (preferente, total ≥ 1500, sin promoción) | No aparece en el BRD | Implementada porque el paquete la exige; marcada como regla de prueba, no de negocio. |
| Anticipo | No existe | Pago total o anticipo mínimo del 50 % (BRD §1 y §4, US-02) | Implementada: `AnticipoMinimoCubierto`. Se exige al inscribir **solo si se informa un pago** (el paquete no trae pagos). |
| Cupo | `capacidad_o_stock` por programa | Mínimo 8, máximo 25 presencial / 40 en línea | Se usa la capacidad del paquete. Los mínimos y máximos por modalidad **no** se modelan en esta iteración. |
| Cancelación | Solo desde SOLICITADA | Cancelación de curso por Administración (cupo mínimo, fuerza mayor) | Solo la del paquete. |
| Liberación por falta de pago (3 días hábiles) | No existe | BRD y US-03 | **No implementada** en esta iteración. |
| Elegibilidad de certificado (asistencia ≥ 80 %, calificación ≥ 70) y bloqueo por saldo | No existe | BRD §1 y §4 (elegibilidad), §6 (saldo), US-13 a US-15, US-20 | **No implementada** en el PIA; se puede agregar como dos Specifications nuevas sin modificar el código actual (ADR-006). |

### Interpretación de las acciones del paquete
El archivo `transiciones_prueba.csv` solo trae el nombre de la acción y los resultados esperados
los conserva el docente. La interpretación aplicada es:

| Acción | Secuencia ejecutada |
|---|---|
| `aprobar` | aceptar |
| `completar` | aceptar → inscribir → finalizar |
| `cancelar` | cancelar |
| `repetir_aprobacion` | aceptar → aceptar (el segundo debe fallar) |
| `saltar_estado` | finalizar directamente desde SOLICITADA (debe fallar) |

## Consecuencias
* (+) El equipo puede explicar al docente cuáles reglas vienen del paquete y cuáles del BRD.
* (−) La trazabilidad BRD → regla → componente → prueba (Integrante 1) tendrá filas del BRD sin
  componente. Quedan listadas arriba como alcance futuro.
