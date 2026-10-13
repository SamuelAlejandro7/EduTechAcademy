# ADR-003: Implementación de Segregación de Responsabilidades de Comandos y Consultas (CQRS Básico)

## Título
Adopción de CQRS Básico para Separar Operaciones Transaccionales de Reportes Administrativos sobre una Base de Datos Compartida.

## Estado
Aceptada

## Contexto
EduTech Academy requiere dos tipos radicalmente diferentes de interacción con el sistema:
1. **Operaciones Transaccionales (Escritura):** Pagos de inscripción, reubicaciones de grupo, rectificación de calificaciones y emisión de folios oficiales. Estas operaciones exigen estricto cumplimiento de invariantes, validación de reglas de negocio complejas y auditoría.
2. **Consultas y Reportes Analíticos (Lectura):** Reportes en tiempo real de ocupación de grupos (US-19: vacantes, inscritos, capacidad según modalidad) y reportes de elegibilidad para Control Escolar (US-18: listados consolidados de alumnos con estatus de nota, asistencia y adeudos).

En la operación manual (*AS-IS*), armar estos reportes en Excel consumía días. La dirección exige que los reportes de ocupación y elegibilidad se generen de manera instantánea y en tiempo real.

## Alternativas
1. **Modelo Unificado Único:**
   * *Descripción:* Utilizar el mismo grafo de objetos del Domain Model tanto para escribir como para consultar.
   * *Consecuencias:* Para renderizar el reporte de ocupación de 20 grupos o el reporte de certificación de 500 alumnos, el sistema tendría que instanciar cientos de Entidades, hidratar Value Objects (`Dinero`, `Calificacion`) y ejecutar lógica de dominio innecesaria. Esto provocaría el problema de consultas $N+1$, alto consumo de memoria y lentitud inaceptable.
2. **CQRS Completo con Bases de Datos Separadas y Event Sourcing:**
   * *Descripción:* Mantener una base de datos relacional para escritura y una base de datos optimizada (NoSQL o vistas materializadas) para lectura, sincronizadas asíncronamente mediante eventos de dominio.
   * *Consecuencias:* Excelente rendimiento y escalabilidad, pero introduce una complejidad arquitectónica desmedida para el tamaño de EduTech Academy (consistencia eventual, infraestructura distribuida y duplicidad de esquemas).
3. **CQRS Básico sobre la Misma Base de Datos Relacional:**
   * *Descripción:* Separar arquitectónicamente las rutas de ejecución en la capa de aplicación:
     * **Commands (Escritura):** Se canalizan a través de `CommandHandlers`, invocan el Domain Model y preservan todas las invariantes transaccionales.
     * **Queries (Lectura):** Se canalizan a través de `QueryHandlers` que realizan proyecciones directas de solo lectura desde las tablas de la base de datos hacia DTOs planos (*View Models*), eludiendo la instanciación de entidades de dominio.

## Decisión
Se decide adoptar la **Alternativa 3: CQRS Básico sobre la misma base de datos relacional**.

Esta arquitectura permite que las pantallas de consulta administrativa y reportes (US-18 y US-19) obtengan datos tabulares optimizados mediante consultas SQL directas y proyecciones a DTOs sin sobrecargar el servidor, mientras que toda la lógica de cambio de estado y protección de reglas permanece 100% resguardada en el Domain Model.

## Consecuencias
* **Beneficios:**
  * Respuestas inmediatas en milisegundos para los reportes administrativos de ocupación y elegibilidad, cumpliendo el criterio de éxito del negocio.
  * Cero riesgo de que una consulta de solo lectura altere accidentalmente el estado de una entidad.
  * Mantiene una arquitectura limpia y comprensible, sin la complejidad operacional de múltiples bases de datos sincronizadas.
* **Costos y Riesgos asumidos:**
  * Duplicación controlada de modelos en la capa de aplicación: coexisten las entidades del dominio (para escritura) y los DTOs de lectura (para vistas de reportes).
  * Los desarrolladores deben disciplinarse para no ejecutar reglas de negocio dentro de los `QueryHandlers`.

## Trazabilidad
* **Necesidades BRD:** Sec. 5 (Disponer de reportes en tiempo real de ocupación de grupos y elegibilidad).
* **Criterios de Éxito:** Sec. 8 (Validación en $< 24$ horas, reporte sin procesos manuales en Excel).
* **Glosario:** Término RN-13 (Elegibilidad de certificación), Término RN-21 (Reporte de ocupación).
* **Historias de Usuario:** US-13, US-18, US-19.