# ADR-009: Domain Events recogidos en el agregado y publicados por la aplicación

* **Estado:** Aceptada
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
El PIA exige Domain Events. Un evento debe existir solo si la transición realmente ocurrió, y
el dominio no debe depender de ningún bus de mensajes ni de infraestructura.

## Decisión
* Los eventos son dataclasses inmutables en pasado: `OperacionAceptada`,
  `BeneficioReferenciaOtorgado`, `OperacionInscrita`, `OperacionFinalizada`,
  `OperacionCancelada`.
* `Operacion` los acumula en una lista interna **después** de cambiar el estado. Si una regla
  falla o la transición es inválida, no se registra ningún evento.
* La capa de aplicación llama a `pull_events()` (entrega y limpia la lista), guarda el agregado
  y publica cada evento mediante el puerto `PublicadorEventos`.
* Cada evento incluye la hora (`ocurrido_en`), que se puede inyectar para pruebas deterministas.
* `BeneficioReferenciaOtorgado` se emite al aceptar cuando se cumple `beneficio_referencia`; así la
  regla del beneficio produce un efecto observable además de poder consultarse.

## Alternativas consideradas
1. **Publicar desde dentro del agregado.** Descartada: acoplaría el dominio a la infraestructura.
2. **Calcular el beneficio solo como consulta.** Descartada: se pierde el hecho de que ocurrió en
   un momento determinado.

## Consecuencias
* (+) Se prueba que un intento fallido no emite eventos (`test_aceptar_exige_puede_procesarse`).
* (+) Infraestructura puede publicar a un log, una cola o una tabla de auditoría sin tocar el dominio.
* (−) Si el guardado falla después de `pull_events()`, los eventos se pierden. En esta iteración se
  publican tras guardar con éxito; un *outbox* queda como mejora.
