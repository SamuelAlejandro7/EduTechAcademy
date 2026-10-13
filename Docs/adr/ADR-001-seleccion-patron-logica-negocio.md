# ADR-001: Selección del Patrón de Lógica de Negocio Principal para EduTech Academy
## Título
Selección del Patrón de Lógica de Negocio Principal para el Proceso de Inscripción, Evaluación y Certificación.
## Estado
Aceptada
## Contexto
En la operación actual (*AS-IS*) de EduTech Academy, la gestión académica depende de cruces manuales en hojas de cálculo de Excel para determinar la elegibilidad de certificación. Esto produce discrepancias frecuentes entre los registros de asistencia y notas, demoras mayores a 24 horas y errores en la aplicación de políticas institucionales. 
El sistema presenta reglas de negocio complejas e interdependientes:
1. Plazo de pago de 3 días hábiles y anticipo mínimo del 50% con liberación automática de plaza.
2. Invariante financiero estricto: retención y bloqueo total de certificados si existe cualquier saldo pendiente ($> 0$).
3. Ventanas temporales estrictas: el instructor solo puede modificar notas dentro de 5 días hábiles tras el cierre; posterior a ello, requiere autorización expresa de Control Escolar.
4. Cruce académico algorítmico: asignación de Certificado ($\ge 80\%$ asistencia y $\ge 70$ puntos), Constancia ($< 80\%$ asistencia y $\ge 70$ puntos) o No Acreditado ($< 70$ puntos).
5. Posibilidad de que cada programa académico modifique o incremente estos umbrales paramétricamente.
## Alternativas
1. **Transaction Script:**
   * *Descripción:* Organizar la lógica en procedimientos o scripts aislados por cada transacción/caso de uso.
   * *Consecuencias:* Bajo costo inicial de desarrollo, pero genera una duplicación descontrolada de reglas críticas (la validación del 50%, la regla de los 5 días y la verificación de saldo cero tendrían que copiarse en múltiples scripts). Favorece un modelo anémico donde un desarrollador puede actualizar el estado de un certificado por SQL sin validar las invariantes.
2. **Table Module:**
   * *Descripción:* Centralizar la lógica en clases asociadas directamente a cada tabla de la base de datos relacional (ej. `InscripcionesTable`, `GruposTable`).
   * *Consecuencias:* Adecuado para aplicaciones centradas puramente en datos tabulares, pero sumamente deficiente cuando una regla atraviesa múltiples conceptos (notas, asistencia, pagos y cupos). Mantiene un alto acoplamiento con la estructura de la base de datos.
3. **Domain Model (Modelo de Dominio):**
   * *Descripción:* Diseñar una red de objetos de dominio ricos que encapsulan conjuntamente datos y comportamiento, protegiendo las invariantes del negocio mediante Entidades, Value Objects y Agregados.
   * *Consecuencias:* Centraliza las reglas en el núcleo del sistema, permitiendo pruebas unitarias automatizadas y exhaustivas independientes de la base de datos. Requiere mayor diseño inicial y una capa de mapeo relacional (ORM/Data Mapper).
## Decisión
Se decide adoptar **Domain Model** como patrón arquitectónico principal para el núcleo transaccional de EduTech Academy.
La justificación técnica radica en que el problema central del negocio no radica en el volumen de datos ni en la persistencia, sino en la **vulnerabilidad de las reglas de negocio**. El Domain Model encapsula las invariantes directamente dentro de las entidades (por ejemplo, el método `inscripcion.emitirCertificado()` valida por diseño que `saldoPendiente == 0` y que la evaluación sea aprobatoria), impidiendo estados inválidos en memoria antes de persistir.
## Consecuencias
* **Beneficios:**
  * Eliminación total de discrepancias entre asistencia y calificaciones mediante un `ServicioCruceElegibilidad` determinista.
  * Blindaje contra la emisión irregular de certificados con saldo deudor.
  * Alta testabilidad y mantenibilidad al evolucionar los umbrales de acreditación por programa sin tocar la persistencia.
* **Costos y Riesgos asumidos:**
  * Desfase objeto-relacional (*Impedance Mismatch*), requiriendo el uso de patrones Repository y Unit of Work para mapear a la base de datos.
  * Curva de aprendizaje y mayor cantidad de código estructural (*boilerplate*) al inicio del proyecto.
  * Sobrecarga de rendimiento si se instancian grafos de objetos ricos para consultas de solo lectura (mitigado mediante CQRS en ADR-003).
## Trazabilidad
* **Necesidades BRD:** Sec. 5 (Eliminar validación manual, consistencia en cupos y plazos).
* **Restricciones y Criterios de Éxito:** Sec. 6 y Sec. 8 (Cero discrepancias, validación en $< 24$ horas).
* **Glosario:** Términos RN-01, RN-02, RN-03, RN-06, RN-09, RN-13, RN-22.
* **Historias de Usuario:** US-02, US-04, US-11, US-13, US-14, US-20. 