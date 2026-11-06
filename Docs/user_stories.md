# Historias de Usuario y Criterios de Aceptación (Gherkin)
## EduTech Academy — Sistema de Gestión Académica y Operativa
**Materia:** Componentes de Lógica de Negocio (UANL - FIME)  
**Equipo:** #15 | **Grupo:** 004  
**Responsable del Documento:** Integrante 1 (Análisis de Negocio, Documentación y Trazabilidad)  
**Versión:** 2.0 (PIA)  

---

## Índice de Historias de Usuario

* **Módulo A: Solicitud, Inscripción y Finanzas (US-01 a US-03, US-20)**
* **Módulo B: Motor de Reglas y Especificaciones del PIA (US-21, US-22)**
* **Módulo C: Administración de Grupos y Cambios de Matrícula (US-04 a US-08)**
* **Módulo D: Gestión Docente y Calificaciones (US-09 a US-12)**
* **Módulo E: Evaluación Académica, Cruce y Certificación (US-13 a US-16)**
* **Módulo F: Capacitación Corporativa y Reportes Analíticos (US-17 a US-19)**

---

## Módulo A: Solicitud, Inscripción y Finanzas

### US-01 · Registro de Solicitud de Curso
**Como** estudiante registrado en la plataforma,  
**quiero** solicitar la inscripción a un programa formativo con cupo disponible,  
**para** apartar mi lugar en el catálogo formativo en estatus inicial `SOLICITADA`.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Solicitud exitosa con cupo disponible
  Given un programa formativo habilitado en el catálogo con cupo disponible > 0
  And un alumno en estatus activo
  When el alumno registra su solicitud de inscripción con al menos una línea de detalle
  Then el sistema crea una operación en estatus "SOLICITADA"
  And emite el evento de dominio "OperacionSolicitada"
```

---

### US-02 · Confirmación de Inscripción con Anticipo Mínimo
**Como** estudiante,  
**quiero** abonar la totalidad o un anticipo mínimo del 50% dentro del plazo de 3 días hábiles,  
**para** pasar mi orden a estado `INSCRITA` y garantizar mi cupo definitivo.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Confirmación de inscripción con anticipo del 50%
  Given una operación en estatus "ACEPTADA" dentro del plazo de 3 días hábiles
  When el estudiante registra un pago igual o mayor al 50% del total de la orden
  Then el sistema cambia el estatus de la operación a "INSCRITA"
  And descuenta formalmente las plazas solicitadas del cupo disponible del programa
  And emite el evento "InscripcionConfirmada"

Scenario: Rechazo por anticipo insuficiente
  Given una operación en estatus "ACEPTADA"
  When el estudiante intenta registrar un pago menor al 50% del costo total
  Then el sistema rechaza la confirmación
  And mantiene la operación en su estatus previo notificando el arancel faltante
```

---

### US-03 · Liberación Automática de Cupo por Vencimiento
**Como** administrador del sistema,  
**quiero** que el sistema cancele automáticamente las solicitudes impagas tras 3 días hábiles,  
**para** liberar las plazas reservadas y ponerlas a disposición de otros estudiantes.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Cancelación automática por falta de pago
  Given una operación en estatus "SOLICITADA" o "ACEPTADA" que cumple más de 3 días hábiles sin pago
  When el proceso de temporización o evaluación de vigencia se ejecuta
  Then el sistema realiza la transición a estatus "CANCELADA"
  And libera cualquier reserva de cupo temporal asociada
  And emite el evento "CupoLiberadoPorExpiracion"
```

---

### US-20 · Bloqueo de Emisión Documental por Saldo Deudor
**Como** personal de Control Escolar,  
**quiero** que el sistema impida emitir certificados o constancias a alumnos con adeudos,  
**para** blindar el cumplimiento de la política de liquidación financiera obligatoria (RN-17 / RN-22).

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Bloqueo de entrega de certificado por saldo pendiente
  Given un alumno dictaminado académicamente como "Elegible para Certificado"
  And la inscripción registra un saldo pendiente mayor a $0 MXN
  When se solicita la emisión o descarga del documento oficial
  Then el sistema bloquea la operación arrojando "SaldoPendienteException"
  And retiene el folio hasta la liquidación total del arancel
```

---

## Módulo B: Motor de Reglas y Especificaciones del PIA

### US-21 · Validación de Precondiciones de Operación (`puede_procesarse`)
**Como** motor de lógica de negocios,  
**quiero** evaluar conjuntamente que el alumno esté activo, que la orden contenga cursos y que tenga autorización,  
**para** autorizar la transición de la operación de `SOLICITADA` a `ACEPTADA`.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Validación exitosa de precondiciones con Specification compuesta
  Given un alumno con activo = 1
  And una operación con detalle_operaciones.count >= 1
  And el atributo autorizado = 1
  When se ejecuta la especificación PuedeProcesarseSpecification
  Then la especificación retorna VERDADERO
  And la operación transita exitosamente al estado "ACEPTADA"

Scenario: Rechazo de operación por alumno inactivo o sin autorización
  Given una operación donde el alumno tiene activo = 0 o autorizado = 0
  When se evalúa PuedeProcesarseSpecification
  Then la especificación retorna FALSO
  And el sistema deniega la transición al estado "ACEPTADA" con código de error de negocio
```

---

### US-22 · Concesión de Beneficio Arancelario VIP (`beneficio_referencia`)
**Como** sistema comercial de EduTech Academy,  
**quiero** otorgar un beneficio de descuento arancelario a clientes preferentes con órdenes mayores a $1,500 MXN sin promociones previas,  
**para** premiar la fidelidad de cuentas corporativas sin duplicar beneficios comerciales.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Concesión exitosa de beneficio arancelario VIP
  Given un alumno con es_preferente = 1
  And una operación con monto total calculado >= 1500.00 MXN
  And el atributo promocion_activa = 0
  When se ejecuta la especificación BeneficioReferenciaSpecification (AND / NOT)
  Then la especificación retorna VERDADERO
  And se aplica el arancel de beneficio preferente a la orden
  And se emite el evento "BeneficioAplicado"

Scenario: Denegación de beneficio por promoción activa concurrente
  Given un alumno con es_preferente = 1 y total >= 1500.00 MXN
  And la operación ya posee promocion_activa = 1
  When se evalúa BeneficioReferenciaSpecification
  Then la especificación retorna FALSO debido a la cláusula NOT promocion_activa
  And se mantiene el importe ordinario sin acumulación de promociones
```

---

## Módulo C: Administración de Grupos y Cambios de Matrícula

### US-04 · Autorización Ordinaria de Cambio de Grupo
**Como** personal de Control Escolar,  
**quiero** autorizar el cambio de grupo de un alumno antes de la 3ª sesión cuando hay cupo,  
**para** reubicar al estudiante manteniendo el orden académico.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Reubicación ordinaria antes de la 3ª sesión
  Given un alumno inscrito en un curso cuya sesión actual es <= 3
  And un grupo de destino con cupo disponible > 0
  When Control Escolar autoriza el cambio de grupo
  Then el sistema libera un cupo en el grupo origen
  And descuenta un cupo en el grupo destino
  And actualiza la matrícula del alumno registrando responsable y fecha
```

---

### US-05 · Cambio de Grupo Excepcional por Fuerza Mayor
**Como** personal de Administración,  
**quiero** aprobar reubicaciones posteriores a la 3ª sesión únicamente por causas justificadas de fuerza mayor,  
**para** resolver situaciones de excepción sin violar las políticas estándar.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Aprobación administrativa por fuerza mayor tras la 3ª sesión
  Given un alumno con solicitud de cambio de grupo posterior a la 3ª sesión
  And una justificación documentada de fuerza mayor
  When Administración emite la autorización formal
  Then el sistema registra el cambio con estatus especial de excepción administrativa
```

---

### US-06 · Cancelación de Grupo por Falta de Cupo Mínimo
**Como** coordinador administrativo,  
**quiero** cancelar los grupos que no alcancen 8 alumnos inscritos a 48 horas del inicio,  
**para** no operar cursos que incumplan la rentabilidad mínima institucional.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Cancelación preventiva por cupo insuficiente
  Given un curso próximo a iniciar en menos de 48 horas con menos de 8 alumnos confirmados
  When el coordinador procede con la cancelación
  Then el estado del grupo y de sus operaciones cambia a "CANCELADA"
  And se habilitan las opciones de reembolso total o cambio de programa
```

---

## Módulo D: Gestión Docente y Calificaciones

### US-11 · Captura y Modificación Oportuna de Calificaciones
**Como** instructor titular,  
**quiero** asentar y ajustar calificaciones dentro de los 5 días hábiles posteriores al cierre,  
**para** corregir posibles erratas de captura sin necesidad de trámites burocráticos.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Modificación permitida dentro de los 5 días hábiles
  Given una evaluación final registrada hace menos de 5 días hábiles
  When el instructor titular ingresa una nueva calificación válida entre 0 y 100
  Then el sistema actualiza la nota en el acta
  And genera la entrada de auditoría correspondiente

Scenario: Modificación bloqueada fuera de plazo ordinario
  Given un acta cerrada hace más de 5 días hábiles
  When el instructor intenta alterar la nota directamente
  Then el sistema bloquea la modificación solicitando autorización expresa de Control Escolar
```

---

### US-12 · Autorización de Rectificación Extemporánea
**Como** personal de Control Escolar,  
**quiero** autorizar rectificaciones extemporáneas de calificaciones solicitadas fuera de plazo,  
**para** preservar la integridad de las actas de estudio.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Rectificación aprobada por Control Escolar
  Given una solicitud de ajuste de nota extemporánea con justificación académica
  When Control Escolar valida y aprueba la corrección
  Then el sistema actualiza la calificación dejando trazabilidad de quién y cuándo autorizó
```

---

## Módulo E: Evaluación Académica, Cruce y Certificación

### US-13 · Cruce Automático de Elegibilidad al Cierre
**Como** sistema de gestión académica,  
**quiero** cruzar automáticamente las asistencias y notas finales al cerrar el curso,  
**para** clasificar a los estudiantes sin depender de revisiones manuales en Excel.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Cruce automático de actas
  Given un programa formativo con evaluaciones y asistencias registradas al 100%
  When el sistema ejecuta el ServicioCruceElegibilidad
  Then clasifica de inmediato a cada estudiante en:
    | Condición                  | Dictamen Resultante          |
    | Asistencia >= 80% y Nota >= 70 | Elegible para Certificado    |
    | Asistencia < 80% y Nota >= 70  | Elegible para Constancia     |
    | Nota < 70                     | No Acreditado                |
```

---

### US-14 · Emisión de Certificado con Folio Único Verificable
**Como** estudiante acreditado,  
**quiero** recibir mi Certificado oficial con un folio alfanumérico irrepetible,  
**para** avalar formalmente mis competencias adquiridas ante terceros y empleadores.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Emisión exitosa de certificado
  Given un estudiante con dictamen "Elegible para Certificado"
  And su cuenta registra saldo pendiente = $0.00 MXN
  When se procesa la emisión del documento
  Then el sistema genera el certificado oficial con nombre, horas, nota y Folio Único
  And emite el evento "CertificadoEmitido"
```

---

### US-15 · Emisión de Constancia de Participación
**Como** estudiante que aprobó académicamente pero con asistencia menor al 80%,  
**quiero** recibir una Constancia de Participación oficial,  
**para** contar con constancia de mi aprovechamiento en el programa.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Emisión de constancia por asistencia insuficiente
  Given un estudiante con nota >= 70 puntos pero asistencia < 80%
  And saldo liquidado ($0 MXN)
  When se solicita la constancia oficial
  Then el sistema emite el documento bajo la modalidad "Constancia de Participación"
```

---

### US-16 · Opción de Recursamiento con Tarifa Reducida
**Como** estudiante no acreditado,  
**quiero** inscribirme para recursar el programa formativo abonando el 50% de la tarifa oficial,  
**para** tener una segunda oportunidad académica accesible.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Recursamiento con 50% de descuento arancelario
  Given un alumno en condición "No Acreditado" en un programa formativo previo
  When solicita cursar nuevamente el programa y existe cupo disponible
  Then el sistema genera una nueva inscripción aplicando automáticamente la tarifa de recursamiento (50% del valor de catálogo)
```

---

## Módulo F: Capacitación Corporativa y Reportes Analíticos

### US-17 · Registro de Matrícula Corporativa B2B
**Como** representante de cuenta empresarial,  
**quiero** registrar a múltiples colaboradores bajo una misma cuenta comercial,  
**para** gestionar la capacitación corporativa con facturación consolidada.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Matrícula corporativa de colaboradores
  Given una cuenta empresarial activa
  When se carga el listado de colaboradores a inscribir
  Then el sistema asocia cada inscripción individual a la cuenta corporativa padre asignando estatus preferente
```

---

### US-18 · Consulta en Tiempo Real de Elegibilidad para Control Escolar
**Como** coordinador de Control Escolar,  
**quiero** consultar el reporte de estudiantes dictaminados en tiempo real,  
**para** acelerar la emisión documental a menos de 24 horas del cierre del acta.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Consulta analítica de elegibilidad
  Given actas cerradas en la base de datos
  When Control Escolar solicita el reporte de elegibilidad
  Then el sistema responde en menos de 2 segundos proyectando DTOs planos con estatus académico y financiero
```

---

### US-19 · Reporte en Tiempo Real de Ocupación de Programas
**Como** director administrativo,  
**quiero** consultar la ocupación y vacantes disponibles de todos los cursos,  
**para** tomar decisiones estratégicas de apertura de nuevos grupos o promociones.

#### Criterios de Aceptación (Gherkin)
```gherkin
Scenario: Consulta masiva de ocupación
  Given los programas formativos del catálogo
  When Administración ejecuta la consulta de ocupación
  Then el sistema proyecta una vista consolidada de plazas ocupadas, vacantes y porcentaje de ocupación
```
