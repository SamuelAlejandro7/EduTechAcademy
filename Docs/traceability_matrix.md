# Matriz de Trazabilidad Integral
## EduTech Academy — Sistema Integral de Gestión Académica y Operativa
**Materia:** Componentes de Lógica de Negocio (UANL - FIME)  
**Equipo:** #15 | **Grupo:** 004  
**Responsable del Documento:** Integrante 1 (Análisis de Negocio, Documentación y Trazabilidad)  
**Versión:** 2.0 (PIA)  

---

## 1. Propósito de la Matriz de Trazabilidad
Esta matriz garantiza la alineación bidireccional continua del software: demuestra cómo cada necesidad comercial del **BRD** se desglosa en **Historias de Usuario**, se valida mediante **Reglas de Negocio / Especificaciones**, se encapsula en **Componentes Arquitectónicos** y se verifica de manera automatizada mediante **Casos de Prueba** (incluyendo los 120 casos y 20 transiciones provistos en los datasets del PIA).

---

## 2. Matriz de Trazabilidad de Requerimientos y Casos de Prueba

| ID Req. (BRD) | Historia de Usuario | Regla / Especificación | Componente / Clase de Dominio | Caso de Prueba / Dataset | Criterio de Aceptación / Estado |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | US-01: Solicitud de Cursos | Precondición de Catálogo | `Operacion` / `DetalleOperacion` | `operaciones.csv`, `detalle_operaciones.csv` | Operación creada en `SOLICITADA` |
| **REQ-02** | US-21: Validación de Operación | `RN-11: puede_procesarse`<br>*(Activo && Detalle >= 1 && Autorizado)* | `PuedeProcesarseSpecification`<br>`src/domain/PuedeProcesarseSpecification` | `casos_prueba.csv`<br>(Casos `EDU-T001` a `EDU-T060`) | Evalúa cliente activo y detalle no vacío $\rightarrow$ `ACEPTADA` |
| **REQ-03** | US-22: Beneficio Preferente VIP | `RN-12: beneficio_referencia`<br>*(VIP && Total >= 1500 && !Promo)* | `BeneficioReferenciaSpecification`<br>`src/domain/BeneficioReferenciaSpecification` | `casos_prueba.csv`<br>(Casos `EDU-B001` a `EDU-B060`) | Descuento preferente aplicado sin duplicidad de promociones |
| **REQ-04** | US-02: Confirmación con Anticipo | `RN-01: Anticipo Mínimo (>= 50%)`<br>`RN-10: Cupo Disponible` | `Inscripcion.confirmarPago()`<br>`Cupo` (Value Object) | `transiciones_prueba.csv`<br>(Acción: `completar`) | Transición `ACEPTADA` $\rightarrow$ `INSCRITA` y cupo descontado |
| **REQ-05** | US-03: Liberación por Vencimiento | `RN-16: Plazo 3 días hábiles` | `Operacion.cancelarPorVencimiento()`<br>`Cupo.liberar()` | `transiciones_prueba.csv`<br>(Acción: `cancelar`) | Transición `SOLICITADA` $\rightarrow$ `CANCELADA` y cupo devuelto |
| **REQ-06** | US-04 / US-05: Cambio de Grupo | `RN-15: Límite 3ª Sesión`<br>`RN-10: Cupo en Destino` | `Grupo.validarCambioGrupo()`<br>`Inscripcion.reubicarGrupo()` | Tests de Dominio / Integración | Reubicación ordinaria $\le 3^a$ sesión o fuerza mayor |
| **REQ-07** | US-11 / US-12: Edición de Calificaciones | `RN-24: Vigencia de 5 días hábiles`<br>`RN-08: Aval Control Escolar` | `EvaluacionFinal.modificarCalificacion()`<br>`VentanaModificacion` (VO) | Tests de Dominio | Instructor edita $\le 5$ días; extemporáneo exige aval |
| **REQ-08** | US-13: Cruce Automático | `RN-02: Asistencia >= 80%`<br>`RN-03: Calificación >= 70` | `ServicioCruceElegibilidad`<br>`src/domain/ServicioCruceElegibilidad` | Tests Unitarios de Dominio | Dictamen tripartita: Certificado / Constancia / No Acreditado |
| **REQ-09** | US-14: Certificado de Acreditación | `RN-06: Folio Único`<br>`RN-17 / RN-22: Saldo Pendiente = $0` | `Certificado` (Aggregate Root)<br>`FolioUnico` (Value Object) | Tests de Dominio | Emisión con Folio Único inmutable tras liquidar arancel |
| **REQ-10** | US-15: Constancia de Participación | `RN-07: Constancia (Asist < 80%)`<br>`RN-17: Saldo Pendiente = $0` | `Certificado` (Tipo: `CONSTANCIA`) | Tests de Dominio | Emisión de constancia si nota $\ge 70$ y asistencia $< 80\%$ |
| **REQ-11** | US-20: Bloqueo por Saldo Pendiente | `RN-17 / RN-22: Bloqueo por Adeudo` | `Inscripcion.validarEmisionCertificado()` | Tests de Excepción / Rollback | Lanza `SaldoPendienteException`; entrega retenida |
| **REQ-12** | US-18 / US-19: Reportes Analíticos | Separación CQRS (Queries) | `ReporteOcupacionQueryHandler`<br>`ReporteElegibilidadQueryHandler` | Tests de API / Integración | Proyección DTOs en tiempo real sin recargar entidades |

---

## 3. Cobertura de las Transiciones de la Máquina de Estados

La siguiente tabla traza los 20 escenarios de transición evaluados en `transiciones_prueba.csv`:

| Caso Transición | Acción Probada | Estado Inicial | Estado Final Esperado | Regla / Invariante Asociada |
| :---: | :---: | :---: | :---: | :--- |
| **EDU-S001** | `completar` | `SOLICITADA` | `ACEPTADA` / `INSCRITA` | Cumple precondición `puede_procesarse` y pago de anticipo |
| **EDU-S002** | `cancelar` | `SOLICITADA` | `CANCELADA` | Solicitud cancelada por alumno o expiración temporal |
| **EDU-S003** | `repetir_aprobacion` | `SOLICITADA` | Excepción / Rechazo | Transición idempotente o duplicada rechazada por máquina de estados |
| *(Casos EDU-S004 a S020)* | Variaciones | Diversos | Conforme a ciclo | Valida que transiciones terminales (`CANCELADA`, `FINALIZADA`) no admitan cambios |

---

## 4. Estado de Dependencias Cruzadas
* **Rutas Técnicas de Clases:** Se actualizarán conforme el **Integrante 2** consolide los archivos de especificación en `src/domain/`.
* **Rutas de Suites de Prueba:** Se actualizarán conforme el **Integrante 3** agregue los archivos en `tests/` para alcanzar la cobertura $\ge 80\%$.
