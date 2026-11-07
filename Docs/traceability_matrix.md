# Matriz de Trazabilidad Integral (End-to-End)
## EduTech Academy — Sistema Integral de Gestión Académica y Operativa
**Materia:** Componentes de Lógica de Negocio (UANL - FIME)  
**Equipo:** #15 | **Grupo:** 004  
**Responsable del Documento:** Integrante 1 (Análisis de Negocio, Documentación y Trazabilidad)  
**Versión:** 3.0 (Cierre Final PIA con Implementación)  

---

## 1. Propósito y Alcance de la Trazabilidad

Esta matriz documenta el alineamiento bidireccional estricto entre:
1. **Requerimientos de Negocio:** Especificados en el `Docs/BRD.md`.
2. **Historias de Usuario y Criterios Gherkin:** Detallados en `Docs/user_stories.md`.
3. **Reglas de Negocio / Especificaciones:** Fórmulas de lógica pura de dominio.
4. **Componentes y Código Fuente:** Clases concretas en `src/Domain/`, `src/Application/` y `src/Api/`.
5. **Decisiones de Arquitectura (ADR):** Justificaciones técnicas en `Docs/adr/`.
6. **Suites de Pruebas y Datasets:** Pruebas automatizadas en `tests/` y resultados de ejecución en `Docs/resultados_pia/`.

---

## 2. Matriz de Trazabilidad por Requerimiento y Módulo

| ID Req. | Historia de Usuario | Regla / Especificación | Componente de Dominio / Aplicación | Contrato API / Endpoint | Suite de Pruebas Automatizadas | Caso de Prueba / Dataset | ADR Asociado |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **REQ-01** | **US-01:** Registro de Solicitud | Precondición de catálogo y creación en estado `SOLICITADA` | `Operacion`<br>(`src/Domain/entities.py`)<br>`LineaOperacion` | `POST /api/v1/operaciones/solicitar`<br>(`src/Api/main.py`) | `tests/domain/test_operacion.py`<br>`tests/test_api.py::test_registrar_solicitud_exitosa` | `operaciones.csv`<br>`detalle_operaciones.csv` | ADR-005<br>ADR-010 |
| **REQ-02** | **US-21:** Validación de Precondiciones | **RN-11 (`puede_procesarse`):**<br>$\text{actor.activo} \land \text{lineas} \ge 1 \land \text{autorizado}$ | `puede_procesarse()`<br>`ActorActivo`<br>`OperacionConLineas`<br>`OperacionAutorizada`<br>(`src/Domain/specifications.py`) | Validación interna en servicio y endpoint (HTTP 201 si cumple, HTTP 422 si falla) | `tests/domain/test_specifications.py`<br>`tests/test_api.py::test_registrar_solicitud_rechazada_por_alumno_inactivo` | `casos_prueba.csv`<br>(60 casos `EDU-T001` a `EDU-T060`)<br>`Docs/resultados_pia/resultados_casos.csv` | ADR-006<br>ADR-010 |
| **REQ-03** | **US-22:** Beneficio Arancelario VIP | **RN-12 (`beneficio_referencia`):**<br>$\text{actor.es\_preferente} \land \text{total} \ge 1500 \land \neg \text{promocion\_activa}$ | `beneficio_referencia()`<br>`ActorPreferente`<br>`TotalMinimo`<br>`PromocionActiva`<br>(`src/Domain/specifications.py`) | `POST /api/v1/operaciones/beneficio`<br>(`src/Api/main.py`) | `tests/domain/test_specifications.py`<br>`tests/test_api.py::test_evaluar_beneficio_vip_exitoso`<br>`tests/test_api.py::test_evaluar_beneficio_vip_denegado_por_promocion_activa` | `casos_prueba.csv`<br>(60 casos `EDU-B001` a `EDU-B060`)<br>`Docs/resultados_pia/resultados_casos.csv` | ADR-006<br>ADR-008 |
| **REQ-04** | **US-02:** Confirmación con Anticipo | **RN-01:** Anticipo mínimo $\ge 50\%$<br>**RN-10:** Cupo disponible | `AnticipoMinimoCubierto`<br>`CapacidadDisponible`<br>`puede_inscribirse()`<br>(`src/Domain/specifications.py`) | `OperacionService.inscribir()`<br>(`src/Application/services.py`) | `tests/domain/test_specifications.py`<br>`tests/application/test_servicios.py` | `transiciones_prueba.csv`<br>(Acción `completar`, ej. `EDU-S001`) | ADR-006<br>ADR-007 |
| **REQ-05** | **US-03:** Liberación por Vencimiento | **RN-16:** Plazo de 3 días hábiles<br>**RN-10:** Devolución de cupo | `siguiente_estado(E.SOLICITADA, Accion.CANCELAR)`<br>(`src/Domain/state_machine.py`) | `OperacionService.cancelar()`<br>(`src/Application/services.py`) | `tests/domain/test_state_machine.py` | `transiciones_prueba.csv`<br>(Acción `cancelar`, ej. `EDU-S002`) | ADR-007 |
| **REQ-06** | **US-04 / US-05:** Cambio de Grupo | **RN-15:** Límite 3ª sesión<br>**RN-10:** Cupo destino | `Grupo.validarCambioGrupo()`<br>`Inscripcion.reubicarGrupo()` | `src/Application/InscripcionApplicationService.hpp` | `tests/domain/test_operacion.py` | Pruebas de integración de dominio | ADR-002 |
| **REQ-07** | **US-11 / US-12:** Edición de Calificaciones | **RN-24:** Vigencia 5 días hábiles<br>**RN-08:** Aval Control Escolar | `EvaluacionFinal.modificarCalificacion()`<br>`VentanaModificacion` | Capa de Dominio | `tests/domain/test_operacion.py` | Pruebas de dominio | ADR-001 |
| **REQ-08** | **US-13:** Cruce Automático de Elegibilidad | **RN-02:** Asistencia $\ge 80\%$<br>**RN-03:** Calificación $\ge 70$ | `ServicioCruceElegibilidad`<br>`Calificacion`<br>`PorcentajeAsistencia` | Capa de Dominio / DTO | `tests/domain/test_value_objects.py` | Evaluaciones finales | ADR-001 |
| **REQ-09** | **US-14 / US-20:** Emisión y Bloqueo de Certificado | **RN-06:** Folio Único<br>**RN-17 / RN-22:** Invariante Saldo = $\$0$ | `Certificado`<br>`FolioUnico`<br>`Inscripcion.validarEmisionCertificado()` | `src/Domain/Inscripcion.cpp`<br>`src/Domain/value_objects.py` | `tests/domain/test_value_objects.py`<br>`tests/application/test_servicios.py` | Casos de prueba de saldo deudor | ADR-001<br>ADR-008 |
| **REQ-10** | **US-15:** Constancia de Participación | **RN-07:** Constancia por asistencia $< 80\%$ con nota aprobatoria | `Certificado`<br>(Tipo `CONSTANCIA`) | Capa de Dominio | `tests/domain/test_value_objects.py` | Evaluaciones con asistencia $< 80\%$ | ADR-001 |
| **REQ-11** | **US-18 / US-19:** Reportes Analíticos | Separación CQRS (Queries directas sin hidratar agregados) | DTOs de lectura plana<br>(`src/Application/dto.py`) | Vistas de consulta rápida | `tests/application/test_servicios.py` | Consultas de ocupación y actas | ADR-003 |

---

## 3. Trazabilidad de la Máquina de Estados (20 Transiciones del PIA)

Todas las transiciones evaluadas en `transiciones_prueba.csv` son gobernadas por la tabla de transiciones en `src/Domain/state_machine.py`:

$$\text{SOLICITADA} \xrightarrow{\text{aceptar}} \text{ACEPTADA} \xrightarrow{\text{inscribir}} \text{INSCRITA} \xrightarrow{\text{finalizar}} \text{FINALIZADA}$$
$$\text{SOLICITADA} \xrightarrow{\text{cancelar}} \text{CANCELADA}$$

| Caso de Prueba | Operación ID | Acción Solicitada | Estado Inicial | Estado Final Obtenido | Resultado Ejecutado | Eventos Emitidos / Excepción Controlada | Archivo de Evidencia |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **EDU-S001** | `EDU-O001` | `completar` | `SOLICITADA` | `FINALIZADA` | **ÉXITO** | `OperacionAceptada` > `OperacionInscrita` > `OperacionFinalizada` | `Docs/resultados_pia/resultados_transiciones.csv` |
| **EDU-S002** | `EDU-O002` | `cancelar` | `SOLICITADA` | `CANCELADA` | **ÉXITO** | `OperacionCancelada` | `Docs/resultados_pia/resultados_transiciones.csv` |
| **EDU-S003** | `EDU-O003` | `repetir_aprobacion` | `SOLICITADA` | `ACEPTADA` | **ERROR CONTROLADO** | Transición inválida capturada: no se puede 'aceptar' en estado `ACEPTADA` | `Docs/resultados_pia/resultados_transiciones.csv` |
| **EDU-S004** | `EDU-O004` | `saltar_estado` | `SOLICITADA` | `SOLICITADA` | **ERROR CONTROLADO** | Transición inválida capturada: no se puede 'finalizar' desde `SOLICITADA` | `Docs/resultados_pia/resultados_transiciones.csv` |
| **EDU-S005 a S020** | `EDU-O005` a `O020` | Variaciones | Diversos | Conforme a regla | **100% CUBIERTAS** | Protege estados terminales y transiciones fuera de orden | `Docs/resultados_pia/resultados_transiciones.csv` |

---

## 4. Trazabilidad de los 120 Casos de Prueba del PIA (`casos_prueba.csv`)

| Tipo de Prueba | Regla Evaluada | Total Casos | Casos que Cumplen | Casos que Incumplen | Motivos de Incumplimiento Identificados | Implementación en Código |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **`validar_operacion`** | `puede_procesarse`<br>(RN-11) | 60 | 48 | 12 | `actor activo`, `operación autorizada`, `operación con al menos una línea` | `PuedeProcesarseSpecification`<br>(`src/Domain/specifications.py`) |
| **`evaluar_beneficio`** | `beneficio_referencia`<br>(RN-12) | 60 | 18 | 42 | `actor preferente`, `total >= 1500`, `promoción activa` (cláusula NOT) | `BeneficioReferenciaSpecification`<br>(`src/Domain/specifications.py`) |
| **TOTAL** | **Homologación Completa** | **120** | **66** | **54** | **100% clasificados y documentados con trazabilidad exacta** | `scripts/ejecutar_casos_pia.py` |

---

## 5. Resumen de Cumplimiento de Calidad
* **Cobertura de Pruebas Automatizadas:** $\ge 80\%$ verificado en el pipeline de GitHub Actions (`ci.yml`).
* **Suite de Pruebas:** Ejecutada con `pytest` y `pytest-cov`.
* **Diseño Arquitectónico:** Avalado por 11 Architecture Decision Records (`ADR-001` a `ADR-011`) y diagramas UML/BPMN en `Diagramas/` y `Docs/bpmn/`.
