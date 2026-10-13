# ADR-002: Desacoplamiento del Agregado Inscripción respecto del Agregado Grupo

## Título
Separación de los Agregados `Inscripcion` y `Grupo` en Límites de Consistencia Independientes.

## Estado
Aceptada

## Contexto
En el modelo conceptual de la Unidad 2, una `Inscripcion` liga a un `Estudiante` con un `Grupo` específico. Cada grupo posee un límite estricto de cupo (25 alumnos en modalidad presencial y 40 en línea, con un mínimo de 8 para apertura). A su vez, los estudiantes disponen de 3 días hábiles para confirmar su lugar mediante el abono de al menos un 50% de anticipo.

Durante periodos de apertura y cobro, ocurren pagos concurrentes de múltiples alumnos para un mismo grupo. Asimismo, se presentan solicitudes de cambio de grupo donde un alumno deja un grupo de origen para integrarse a un grupo de destino antes de la 3ª sesión.

## Alternativas
1. **Modelo Jerárquico Único (Agregado `Grupo` contenedor):**
   * *Descripción:* Modelar `Grupo` como la única raíz de agregado (*Aggregate Root*), conteniendo internamente una lista de todas las entidades `Inscripcion` asociadas a él.
   * *Consecuencias:* Garantiza consistencia inmediata y atómica en el cálculo del cupo. Sin embargo, impone un cuello de botella grave de concurrencia: cada vez que un estudiante abona un pago parcial, se bloquea transaccionalmente la entidad `Grupo` completa, impidiendo que otros alumnos paguen o reserven en ese grupo simultáneamente.
2. **Agregados Separados con Referencias por Identificador (`GrupoId`):**
   * *Descripción:* Definir `Grupo` e `Inscripcion` como dos Agregados independientes. `Grupo` custodia exclusivamente su ciclo de vida y su Value Object `Cupo` (mínimo, máximo, ocupado). `Inscripcion` custodia el ciclo de vida del estudiante, su cronograma de pagos y su saldo pendiente, manteniendo únicamente una referencia escalar `GrupoId`.
   * *Consecuencias:* Desacopla las transacciones financieras individuales del control global de capacidad del grupo, optimizando la concurrencia.

## Decisión
Se decide adoptar la **Alternativa 2: Separar `Inscripcion` y `Grupo` como Agregados independientes**, comunicados y coordinados a través de la capa de aplicación (*Application Services*) y referenciados únicamente por sus identificadores únicos (`InscripcionId` y `GrupoId`).

La razón determinante es el rendimiento y la escalabilidad: las operaciones financieras (registro de abonos, control de plazos de 3 días) no deben competir por bloqueos de base de datos contra el control de cupo general del grupo.

## Consecuencias
* **Beneficios:**
  * Alta concurrencia: múltiples estudiantes pueden confirmar sus inscripciones y registrar pagos concurrentemente sin colisiones de bloqueo.
  * Fronteras de consistencia pequeñas y transacciones más cortas y limpias.
  * Simplificación del ciclo de vida de `Inscripcion` (estados: *Preinscrita, Inscrita, Reubicada, Cancelada*).
* **Costos y Riesgos asumidos:**
  * Las operaciones que involucran a ambos agregados —como un cambio de grupo o una liberación de plaza por falta de pago— requieren coordinar dos agregados distintos mediante la capa de aplicación y el patrón *Unit of Work*, asegurando que la liberación del cupo en el grupo y la cancelación de la inscripción se sincronicen correctamente.

## Trazabilidad
* **Necesidades BRD:** Sec. 4 (Gestión de cupos, confirmación de pagos y cambios de grupo).
* **Restricciones:** Sec. 6 (Cupo mín 8, máx 25/40, plazo de 3 días hábiles).
* **Glosario:** Términos RN-10 (Cupo disponible), RN-11 (Cupo máximo), RN-17 (Liberación de cupo), RN-23 (3ª sesión límite).
* **Historias de Usuario:** US-01, US-02, US-03, US-04, US-05.