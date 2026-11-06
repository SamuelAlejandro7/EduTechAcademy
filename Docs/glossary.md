# Glosario de Términos del Dominio (Lenguaje Ubicuo)
## EduTech Academy — Producto Integrador de Aprendizaje (PIA)
**Materia:** Componentes de Lógica de Negocio  
**Facultad:** Facultad de Ingeniería Mecánica y Eléctrica (FIME - UANL)  
**Equipo:** #15 | **Grupo:** 004  
**Responsable del Documento:** Integrante 1 (Análisis de Negocio, Documentación y Trazabilidad)

---

## 1. Introducción y Propósito
El presente glosario formaliza el **Lenguaje Ubicuo** (*Ubiquitous Language*) para el sistema de gestión académica y operativa de **EduTech Academy** (Giro: Capacitación Digital). El propósito fundamental es garantizar una semántica rigurosa, unívoca y compartida entre analistas de negocio, arquitectos de software, desarrolladores y personal operativo, erradicando ambigüedades en el código, en la documentación y en los casos de prueba.

---

## 2. Entidades Principales y Agregados del Negocio

### 2.1. Alumno (Actor Principal)
* **Definición:** Persona física o colaborador corporativo registrado en la plataforma que solicita y cursa programas formativos.
* **Identificador:** `actor_id` (Formato alfanumérico estandarizado: `EDU-C001` a `EDU-C040`).
* **Atributos Clave:**
  * `nombre`: Nombre o identificador formal del estudiante.
  * `activo`: Bandera booleana (`1` = Activo, `0` = Inactivo/Suspendido). Condición obligatoria para cualquier operación válida.
  * `es_preferente` (VIP): Indicador booleano que clasifica al alumno como preferente o corporativo, habilitando elegibilidad para beneficios de descuento.
  * `ciudad`: Ubicación geográfica o sede de residencia del alumno (ej. Monterrey, Apodaca, San Nicolás, etc.).

### 2.2. Programa Formativo / Curso (Recurso Principal)
* **Definición:** Oferta educativa especializada en tecnologías digitales (ej. Cloud Computing, Data Science, Ciberseguridad, Desarrollo de Software, IA).
* **Identificador:** `recurso_id` (Formato alfanumérico: `EDU-P001` a `EDU-P020`).
* **Atributos Clave:**
  * `descripcion`: Nombre descriptivo del curso o taller formativo.
  * `precio_mxn`: Valor arancelario unitario expresado en pesos mexicanos mediante tipo `Decimal`.
  * `capacidad_o_stock`: Límite máximo de plazas o cupo disponible asignado al programa.
  * `habilitado`: Bandera booleana (`1` = Disponible en catálogo, `0` = Deshabilitado/Cerrado).

### 2.3. Operación / Inscripción (Aggregate Root)
* **Definición:** Instancia transaccional que agrupa la solicitud de uno o varios programas formativos por parte de un alumno, gobernando su ciclo de vida y sus obligaciones financieras.
* **Identificador:** `operacion_id` (Formato alfanumérico: `EDU-O001` a `EDU-O060`).
* **Atributos Clave:**
  * `actor_id`: Clave foránea al alumno titular.
  * `estado`: Estado actual dentro de la máquina de estados del negocio.
  * `fecha_solicitud`: Fecha de emisión en formato ISO 8601 (`YYYY-MM-DD`).
  * `promocion_activa`: Bandera que indica si la orden goza de una promoción comercial externa preexistente.
  * `autorizado`: Bandera booleana que acredita la validación administrativa de la operación.
  * `referencia`: Código alfanumérico único para auditoría contable (ej. `PIA_EDU_001`).

### 2.4. Detalle de Operación (Línea de Inscripción)
* **Definición:** Elemento subordinado a la `Operacion` que vincula un `ProgramaFormativo` específico con la cantidad de plazas requeridas.
* **Atributos Clave:**
  * `operacion_id`: Referencia a la operación padre.
  * `recurso_id`: Referencia al curso seleccionado.
  * `cantidad`: Entero positivo ($\ge 1$) que representa el número de inscripciones solicitadas.

---

## 3. Objetos de Valor (Value Objects)

* **`Dinero`:** Objeto inmutable que modela importes monetarios en MXN, encapsulando operaciones aritméticas de suma, resta y multiplicación por factores sin pérdida de precisión decimal.
* **`Cupo`:** Objeto de valor que resguarda la capacidad mínima (8 alumnos), capacidad máxima (25 presencial / 40 online) y disponibilidad en tiempo real, impidiendo sobrecupos (*overbooking*).
* **`Calificacion`:** Valor numérico entero o decimal en escala de $0$ a $100$ puntos. Determina si el puntaje es aprobatorio ($\ge 70$ puntos o criterio específico de programa).
* **`PorcentajeAsistencia`:** Valor porcentual $[0\%, 100\%]$. Evalúa el cumplimiento del umbral mínimo institucional ($80\%$).
* **`FolioUnico`:** Código alfanumérico irrepetible asignado a certificados y constancias oficiales para permitir su verificación pública.
* **`VentanaModificacion`:** Intervalo temporal estricto de 5 días hábiles posteriores al cierre de calificaciones en el cual un instructor puede rectificar notas directamente.

---

## 4. Máquina de Estados del Ciclo de Vida de la Operación

Las operaciones formativas transitan por los siguientes estados discretos, protegidos por invariantes que rechazan cualquier transición no autorizada:

1. **`SOLICITADA`:**
   * Estado inicial por defecto de toda operación al registrarse en el sistema.
   * La solicitud ha sido creada, pero aún no se han verificado precondiciones ni recibido pagos.
2. **`ACEPTADA`:**
   * La operación ha superado con éxito la especificación de precondiciones (`puede_procesarse`), confirmando alumno activo, detalle no vacío y autorización administrativa.
3. **`INSCRITA`:**
   * El pago o anticipo mínimo institucional ($\ge 50\%$) ha sido validado dentro del plazo de 3 días hábiles. El cupo del programa formativo queda formalmente reservado y descontado.
4. **`FINALIZADA`:**
   * El alumno ha cursado el programa, se han registrado calificaciones/asistencia y se ha dictaminado su elegibilidad documental (Certificado o Constancia).
5. **`CANCELADA`:**
   * Transición terminal alternativa. Ocurre por:
     * Falta de pago en el plazo de 3 días hábiles (liberación automática de cupo).
     * Solicitud explícita de cancelación o cupo mínimo no alcanzado a 48h del inicio.
     * Causa de fuerza mayor dictaminada por Administración.

---

## 5. Reglas de Negocio y Especificaciones (Specification Pattern)

### 5.1. Regla `puede_procesarse` (Validación de Operación)
* **Definición:** Especificación compuesta que dictamina si una operación en estado `SOLICITADA` reúne las precondiciones necesarias para avanzar.
* **Fórmula Lógica:**
  $$\text{puede\_procesarse} = (\text{actor.activo} == 1) \land (\text{detalle.count} \ge 1) \land (\text{operacion.autorizado} == 1)$$
* **Resultado:** Si es verdadera, la operación puede pasar a `ACEPTADA`. Si es falsa, el sistema rechaza la transición y notifica la causa de rechazo.

### 5.2. Regla `beneficio_referencia` (Evaluación de Beneficio VIP)
* **Definición:** Especificación de negocio combinada con operadores lógicos `AND` y `NOT` para otorgar descuentos comerciales preferentes.
* **Fórmula Lógica:**
  $$\text{beneficio\_referencia} = (\text{actor.es\_preferente} == 1) \land (\text{total\_mxn} \ge 1500.00) \land \neg(\text{operacion.promocion\_activa} == 1)$$
* **Resultado:** Si se cumple, habilita un beneficio arancelario de cliente preferente. Se deniega si el alumno no es preferente, si el total es menor a $1,500 MXN o si la operación ya goza de otra promoción comercial activa (evitando acumulación indebida de beneficios).

### 5.3. Regla del Anticipo Mínimo (RN-01)
* Pago requerido equivalente al menos al $50\%$ del costo total del programa dentro de los 3 días hábiles siguientes a la solicitud para asegurar la inscripción.

### 5.4. Regla de Bloqueo por Saldo Pendiente (RN-22)
* Ningún certificado de acreditación ni constancia oficial puede emitirse mientras la cuenta del alumno mantenga un `SaldoPendiente > 0`.

### 5.5. Regla del Cruce Automático de Elegibilidad (RN-02, RN-03, RN-13)
* Evaluación determinista al cierre del curso:
  * **Elegible para Certificado:** Asistencia $\ge 80\%$ **Y** Calificación $\ge 70$.
  * **Elegible para Constancia:** Asistencia $< 80\%$ **Y** Calificación $\ge 70$.
  * **No Acreditado:** Calificación $< 70$.

---

## 6. Roles y Actores del Negocio

* **Alumno / Estudiante:** Solicita programas formativos, realiza pagos, cursa contenidos y recibe documentación oficial.
* **Instructor Titular:** Imparte el curso, toma asistencia y registra notas finales (con ventana de 5 días hábiles para ajustes).
* **Control Escolar:** Valida elegibilidad académica, autoriza correcciones extemporáneas de calificaciones y gestiona cambios de grupo dentro del límite ordinario (hasta 3ª sesión).
* **Administración:** Autoriza cancelaciones de grupo, aprueba sustitución formal de instructores y convalida excepciones de fuerza mayor.
* **Cliente Empresarial:** Cuenta corporativa que inscribe a múltiples colaboradores preferentes bajo una orden de compra o contrato corporativo.

---

## 7. Eventos de Dominio (Domain Events)

* `OperacionSolicitada`: Registro inicial de solicitud de cursos con detalle de programas.
* `OperacionAceptada`: Validación satisfactoria de precondiciones (`puede_procesarse`).
* `InscripcionConfirmada`: Abono validado ($\ge 50\%$) y plazas descontadas del cupo.
* `CupoLiberadoPorExpiracion`: Cancelación automática de solicitud por impago tras 3 días hábiles.
* `BeneficioAplicado`: Concesión de descuento preferente tras validar especificación VIP.
* `ElegibilidadDeterminada`: Cruce automático completado con clasificación tripartita.
* `CertificadoEmitido`: Generación formal de certificado con folio único inmutable.
* `EmisionBloqueadaPorSaldo`: Alumno acreditado académicamente con entrega documental retenida por adeudo.
