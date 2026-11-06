# ADR-010: Taxonomía de errores y mapeo sugerido a HTTP

* **Estado:** Aceptada (el contrato final de la API lo confirma el Integrante 3)
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
El paquete pide contrastar respuestas de la API con 200/201, 400/409/422 y 404 según el contrato
del equipo. El dominio no debe conocer HTTP, pero la API necesita distinguir los tipos de fallo
de forma estable.

## Decisión
Todos los errores de negocio heredan de `ErrorDeDominio` y llevan un `codigo` estable y una tupla
`motivos`. Se agrupan en dos familias, más un error de la capa de aplicación:

| Familia | Errores | Significado | HTTP sugerido |
|---|---|---|---|
| `ErrorDeValidacion` | `CantidadInvalida`, `ImporteInvalido`, `RecursoNoHabilitado`, `OperacionNoProcesable`, `InscripcionNoPermitida` | La petición viola una regla de negocio | 422 |
| `ErrorDeEstado` | `TransicionInvalida`, `CapacidadInsuficiente`, `OperacionNoModificable` | La petición choca con el estado actual | 409 |
| `EntidadNoEncontrada` | actor, recurso u operación inexistente | El identificador no existe | 404 |

Respuestas exitosas sugeridas: `POST /operaciones` → 201; consultas y acciones → 200.
Un 400 corresponde a peticiones mal formadas (JSON inválido, campos faltantes) y lo detecta el
esquema de la API antes de llegar al dominio.

El cuerpo de error sugerido es `{"codigo": error.codigo, "mensaje": error.mensaje, "motivos": [...]}`.

## Alternativas consideradas
1. **Códigos de estado dentro del dominio.** Descartada: acopla el dominio al protocolo.
2. **Una sola excepción genérica.** Descartada: la API no podría distinguir 409 de 422 sin leer texto.

## Consecuencias
* (+) La API traduce errores con un solo manejador por familia.
* (+) Los `motivos` permiten mensajes concretos ("actor activo", "operación autorizada").
* (−) Si el contrato del Integrante 3 usa otros códigos (por ejemplo 400 en lugar de 422), solo
  cambia la tabla de mapeo, no el dominio.
