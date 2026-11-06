# Modelado de Procesos de Negocio (BPMN)
## EduTech Academy — Sistema Integral de Gestión Académica y Operativa
**Materia:** Componentes de Lógica de Negocio (UANL - FIME)  
**Equipo:** #15 | **Grupo:** 004  
**Responsable del Documento:** Integrante 1 (Análisis de Negocio, Documentación y Trazabilidad)  

---

## 1. Descripción General del Proceso

El modelo BPMN de EduTech Academy documenta el ciclo de vida completo de la capacitación digital, articulando la interacción entre los 5 roles clave del sistema:
1. **Alumno / Estudiante:** Actor externo que selecciona programas, solicita inscripción y cancela aranceles.
2. **Motor de Reglas & Dominio (Sistema):** Núcleo transaccional que valida precondiciones mediante especificaciones (`puede_procesarse`, `beneficio_referencia`), administra la máquina de estados y ejecuta el cruce automático.
3. **Instructor:** Docente responsable de la impartición, control de asistencia y registro de actas de evaluación.
4. **Control Escolar:** Validador de cambios de grupo ordinarios ($\le 3^a$ sesión) y autorizaciones extemporáneas de calificaciones.
5. **Administración:** Instancia de gobierno para cancelaciones por falta de cupo mínimo y excepciones de fuerza mayor.

---

## 2. Fases del Flujo de Negocio

### Fase 1: Solicitud y Validación de Precondiciones
* **Evento Inicial:** El alumno selecciona uno o más cursos del catálogo y registra su solicitud.
* **Estado:** La orden ingresa en estatus `SOLICITADA`.
* **Compuerta de Negocio:** Se evalúa la regla `puede_procesarse`:
  * Alumno activo ($== 1$).
  * Detalle con al menos 1 línea de curso.
  * Solicitud autorizada ($== 1$).
* **Resolución:** Si no cumple, se rechaza la solicitud (HTTP 422). Si cumple, transita a `ACEPTADA` y se evalúa el beneficio preferente (`beneficio_referencia`: VIP, total $\ge \$1,500\text{ MXN}$ y sin otra promoción concurrente).

### Fase 2: Control Financiero y Cupo
* **Compuerta Temporal:** Se otorga una ventana máxima de 3 días hábiles para el pago.
* **Excepción de Impago:** Si expiran los 3 días hábiles sin pago, el sistema transita a `CANCELADA` y libera cualquier reserva temporal.
* **Flujo Normal:** Si se registra un pago $\ge 50\%$ de anticipo, la operación transita a `INSCRITA` y se descuentan formalmente las plazas del cupo disponible del programa formativo.

### Fase 3: Impartición y Modificaciones Académicas
* El instructor registra asistencias y notas.
* **Subproceso de Cambio de Grupo:**
  * Si la sesión actual es $\le 3$ y hay cupo disponible, Control Escolar autoriza la reubicación ordinaria.
  * Si la sesión actual es $> 3$, solo la Administración puede validar el cambio bajo causal comprobable de fuerza mayor.
* **Cierre de Actas:** El docente tiene una ventana ordinaria de 5 días hábiles para ajustes. Vencido este plazo, cualquier rectificación requiere la aprobación de Control Escolar.

### Fase 4: Cruce Automático de Elegibilidad y Emisión Documental
* **Cruce Determinista:** Se ejecuta el `ServicioCruceElegibilidad`:
  1. Si nota $< 70$ puntos: Dictamen `NO ACREDITADO`. Se notifica al estudiante y se habilita la opción de recursamiento con 50% de arancel.
  2. Si nota $\ge 70$ y asistencia $< 80\%$: Dictamen `ELEGIBLE PARA CONSTANCIA`.
  3. Si nota $\ge 70$ y asistencia $\ge 80\%$: Dictamen `ELEGIBLE PARA CERTIFICADO`.
* **Invariante Financiero (RN-22 / RN-17):**
  * Si `SaldoPendiente > $0`: La emisión y entrega del documento oficial (Certificado o Constancia) queda estrictamente bloqueada hasta la liquidación total.
  * Si `SaldoPendiente == $0`: Se genera el documento con su **Folio Único Verificable** irrepetible y la operación transita a `FINALIZADA`.

---

## 3. Archivos Fuente Disponibles

* `bpmn_proceso_principal.puml`: Archivo fuente en PlantUML para renderizado detallado con carril de actores y participantes.
* `bpmn_proceso_principal.mmd`: Archivo fuente en Mermaid para previsualización interactiva automática en GitHub.
