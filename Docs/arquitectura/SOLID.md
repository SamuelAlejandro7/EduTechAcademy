# Justificación SOLID

Cada principio se muestra con el código real del proyecto y con la prueba que lo respalda.

## S — Responsabilidad única

Cada clase tiene una sola razón para cambiar.

| Clase / módulo | Única responsabilidad |
|---|---|
| `Dinero` | Representar y operar importes con `Decimal` |
| `Cantidad` | Garantizar un entero positivo |
| `ActorActivo`, `TotalMinimo`, `PromocionActiva`... | Evaluar **una** condición cada una |
| `state_machine.py` | Decidir qué transiciones son válidas |
| `Operacion` | Proteger los invariantes del agregado y registrar eventos |
| `ServicioOperaciones` | Orquestar: cargar, llamar al dominio, guardar, publicar. No contiene reglas |

Prueba: si cambia el umbral de 1500 MXN, solo se toca `TotalMinimo`/`UMBRAL_BENEFICIO`; si cambia
el flujo de estados, solo la tabla `TRANSICIONES`.

## O — Abierto/cerrado

Abierto a extensión, cerrado a modificación.

* **Nueva regla de negocio:** se agrega una clase que hereda de `Specification` y se combina con
  `&`, `|` o `~`. No se modifica ninguna clase existente. Ejemplo: la regla del BRD
  `AnticipoMinimoCubierto` se sumó a `puede_inscribirse()` sin tocar las demás reglas.
* **Nueva transición:** se agrega una fila a `TRANSICIONES`.
* **Nuevo evento:** se agrega una dataclass que hereda de `EventoDeDominio`.
* **Nuevo almacenamiento:** se implementa un repositorio nuevo (CSV, SQL); el dominio no cambia.

## L — Sustitución de Liskov

Cualquier subtipo puede usarse donde se espera su tipo base.

* `And`, `Or` y `Not` reciben `Specification` y funcionan igual con cualquier regla simple o
  compuesta, porque todas respetan el contrato `is_satisfied_by(ctx) -> bool`.
* Los repositorios en memoria de las pruebas (`tests/fakes.py`) sustituyen a los reales sin que
  `ServicioOperaciones` lo note.

Prueba: `test_and_or_not_se_combinan_con_operadores` combina reglas distintas con los tres operadores.

## I — Segregación de interfaces

Interfaces pequeñas, hechas a la medida de quien las usa.

* `ActorRepository` solo tiene `obtener` (el sistema no modifica actores).
* `RecursoRepository` tiene `obtener` y `guardar` (se reserva cupo).
* `OperacionRepository` tiene `obtener` y `guardar`.
* `PublicadorEventos` tiene un único método, `publicar`.

No existe un "repositorio universal" que obligue a implementar métodos que no se usan.

## D — Inversión de dependencias

Los módulos de alto nivel dependen de abstracciones, no de detalles.

* `ServicioOperaciones` recibe sus repositorios y su publicador por el constructor, como interfaces
  (`ActorRepository`, `RecursoRepository`, `OperacionRepository`, `PublicadorEventos`).
* Las interfaces de repositorio están definidas **en el dominio**, y las implementa infraestructura.
* `src/Domain` no importa nada de `src/Application`, `src/Infrastructure` ni `src/api`
  (verificado con `grep`).

Prueba: toda la suite de `tests/application` corre con repositorios en memoria, sin base de datos.
