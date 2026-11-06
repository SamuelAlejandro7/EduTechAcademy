# Guía de integración para el equipo

Documento para el **Integrante 1** (trazabilidad) y el **Integrante 3** (API, infraestructura y pruebas).

## 1. Componentes y rutas (para la matriz de trazabilidad)

| Regla / requisito | Componente | Archivo | Pruebas |
|---|---|---|---|
| `puede_procesarse` | `puede_procesarse()`, `ActorActivo`, `OperacionConLineas`, `OperacionAutorizada` | `src/Domain/specifications.py` | `tests/domain/test_specifications.py`, `tests/domain/test_operacion.py`, `tests/application/test_servicios.py` |
| `beneficio_referencia` | `beneficio_referencia()`, `ActorPreferente`, `TotalMinimo`, `PromocionActiva` | `src/Domain/specifications.py` | `tests/domain/test_specifications.py`, `tests/application/test_servicios.py` |
| Precondiciones de inscripción | `puede_inscribirse()`, `RecursosHabilitados`, `CapacidadDisponible` | `src/Domain/specifications.py` | `tests/domain/test_specifications.py`, `tests/domain/test_operacion.py` |
| Anticipo mínimo del 50 % (BRD, US-02) | `AnticipoMinimoCubierto` | `src/Domain/specifications.py` | `tests/domain/test_specifications.py`, `tests/application/test_servicios.py` |
| Máquina de estados | `TRANSICIONES`, `siguiente_estado` | `src/Domain/state_machine.py` | `tests/domain/test_state_machine.py` |
| Transiciones inválidas | `TransicionInvalida` | `src/Domain/errors.py` | `tests/domain/test_operacion.py`, `tests/application/test_servicios.py` |
| Domain Events | `OperacionAceptada`, `BeneficioReferenciaOtorgado`, `OperacionInscrita`, `OperacionFinalizada`, `OperacionCancelada` | `src/Domain/events.py` | `tests/domain/test_operacion.py`, `tests/application/test_servicios.py` |
| Total con `Decimal` | `Dinero`, `Operacion.total()` | `src/Domain/value_objects.py`, `src/Domain/entities.py` | `tests/domain/test_value_objects.py`, `tests/domain/test_operacion.py` |
| Validación de cantidades | `Cantidad` | `src/Domain/value_objects.py` | `tests/domain/test_value_objects.py` |
| Disponibilidad / capacidad | `RecursoFormativo.reservar`, `Operacion.agregar_linea` | `src/Domain/entities.py` | `tests/domain/test_operacion.py` |
| Casos de uso | `ServicioOperaciones` | `src/Application/services.py` | `tests/application/test_servicios.py` |

Reglas del BRD **sin componente en esta iteración** (ver ADR-011): liberación por falta de pago a
3 días hábiles, elegibilidad de certificado (asistencia ≥ 80 %, calificación ≥ 70), bloqueo por
saldo pendiente, cupos mínimo/máximo por modalidad.

## 2. Para el Integrante 3: qué debes implementar y consumir

### 2.1 Repositorios (puertos en `src/Domain/repositories.py`)

| Interfaz | Métodos | Notas |
|---|---|---|
| `ActorRepository` | `obtener(actor_id) -> Actor \| None` | Devuelve `None` si no existe |
| `RecursoRepository` | `obtener(recurso_id) -> RecursoFormativo \| None`, `guardar(recurso)` | `guardar` persiste el cupo reservado |
| `OperacionRepository` | `obtener(operacion_id) -> Operacion \| None`, `guardar(operacion)` | Guardar estado y líneas |

Para construir las entidades desde los CSV se puede copiar la función `cargar()` de
`scripts/ejecutar_casos_pia.py`. Puntos a respetar:
* Los importes se construyen con `Dinero.de("566")` (desde texto o entero, nunca `float`).
* Las banderas `0/1` se convierten a `bool`.
* Una operación puede no tener líneas (EDU-O013, EDU-O039) y debe cargarse igual: el dominio la
  rechaza con `OperacionNoProcesable`, no con un error de carga.
* Un recurso deshabilitado (EDU-P011) también puede aparecer en líneas existentes.

### 2.2 Casos de uso (`src/Application/services.py`)

```python
servicio = ServicioOperaciones(actores, recursos, operaciones, publicador)
```

| Método | Entrada | Salida | Endpoint sugerido |
|---|---|---|---|
| `solicitar_operacion(cmd)` | `SolicitarOperacionCommand` | `OperacionDTO` | `POST /operaciones` → 201 |
| `obtener_operacion(id)` | `str` | `OperacionDTO` | `GET /operaciones/{id}` → 200 |
| `validar_operacion(id)` | `str` | `ResultadoRegla` | `GET /operaciones/{id}/validacion` → 200 |
| `evaluar_beneficio(id)` | `str` | `ResultadoRegla` | `GET /operaciones/{id}/beneficio` → 200 |
| `aplicar_accion(cmd)` | `AplicarAccionCommand` | `ResultadoTransicion` | `POST /operaciones/{id}/acciones` → 200 |

Los DTOs están en `src/Application/dto.py`. Los importes son `Decimal`: se recomienda serializarlos
como texto (`"1600.00"`) para no perder precisión.

`AplicarAccionCommand.accion` es un `Accion` (`ACEPTAR`, `INSCRIBIR`, `FINALIZAR`, `CANCELAR`).
Si en `INSCRIBIR` se informa `monto_pagado`, se exige el anticipo mínimo del 50 %.

### 2.3 Errores → respuestas HTTP (propuesta, ver ADR-010)

| Error | HTTP | Cuándo |
|---|---|---|
| `ErrorDeValidacion` (y subtipos) | 422 | Regla de negocio incumplida |
| `ErrorDeEstado` (y subtipos) | 409 | Transición inválida, cupo insuficiente |
| `EntidadNoEncontrada` | 404 | Actor, recurso u operación inexistente |
| JSON mal formado / campos faltantes | 400 | Lo detecta el esquema de la API |

Cuerpo sugerido: `{"codigo": e.codigo, "mensaje": e.mensaje, "motivos": list(e.motivos)}`.

### 2.4 Pruebas

* Mis pruebas están en `tests/domain/` y `tests/application/` (99 pruebas, cobertura 100 % de `src/`).
  Para no pisar el trabajo del Integrante 3, no tocan otros archivos de `tests/`.
* `tests/fakes.py` tiene repositorios y publicador en memoria **solo para pruebas**.
* Para la API se puede reutilizar `ServicioOperaciones` con esos dobles.
* `pyproject.toml` (raíz, nuevo): configuración de pytest, cobertura y ruff. Este paquete solo usa la librería estándar; no agrega dependencias.
* Compatible con Python 3.10, la versión del CI (`.github/workflows`). Se probó con el mismo comando del CI: `pytest --cov=src --cov-fail-under=80`.
* La cobertura del CI se mide sobre **todo** `src/`: el código de infraestructura y API del Integrante 3 también debe tener pruebas para que el total no baje de 80 %.
* `ruff check src tests scripts` pasa sin errores con ruff 0.16.8 (el CI actual no ejecuta ruff, pero conviene mantenerlo limpio).

## 3. Resultados de los casos del paquete

Se ejecutaron con `python scripts/ejecutar_casos_pia.py RUTA_A_LOS_CSV Docs/resultados_pia`.
Los resultados esperados los conserva el docente; estas son las salidas reales del dominio
(archivos `Docs/resultados_pia/resultados_casos.csv` y `Docs/resultados_pia/resultados_transiciones.csv`).

### 3.1 `casos_prueba.csv` (120 casos)

| Tipo | Cumple | No cumple |
|---|---|---|
| `validar_operacion` (`puede_procesarse`) | 46 | 14 |
| `evaluar_beneficio` (`beneficio_referencia`) | 10 | 50 |

Las 14 operaciones que no cumplen `puede_procesarse` coinciden exactamente con las anomalías de los
datos: 7 sin autorización, 5 con actor inactivo y 2 sin líneas.

### 3.2 `transiciones_prueba.csv` (20 casos)

| Acción | Casos | Resultado |
|---|---|---|
| `aprobar` | 4 | 4 exitosas (ACEPTADA) |
| `cancelar` | 4 | 4 exitosas (CANCELADA) |
| `completar` | 4 | 3 exitosas (FINALIZADA); 1 con `OPERACION_NO_PROCESABLE` (EDU-S016, sin autorización) |
| `repetir_aprobacion` | 4 | 4 con error: 2 `TRANSICION_INVALIDA` (EDU-S003, EDU-S018) y 2 `OPERACION_NO_PROCESABLE` (EDU-S008, EDU-S013) |
| `saltar_estado` | 4 | 4 con `TRANSICION_INVALIDA` |

## 4. Correspondencia con la documentación de EduTech (Integrante 1)

Los nombres de código difieren de los del glosario porque el paquete de pruebas del PIA es genérico:

| Glosario / BRD | Código |
|---|---|
| Alumno | `Actor` |
| ProgramaFormativo / Cupo | `RecursoFormativo` (`reservar()` descuenta cupo) |
| Inscripción | `Operacion` (raíz de agregado) |

| Regla (BRD / matriz) | Dónde vive en el código |
|---|---|
| RN-01 anticipo | `Operacion.inscribir(..., monto_pagado)` + `puede_inscribirse(exigir_anticipo=True)` |
| RN-02 / RN-03 cruce de horario | Specifications en `src/Domain/specifications.py` |
| RN-10 cupo | `RecursoFormativo.reservar()` |
| RN-11 procesabilidad | `Operacion.aceptar()` → `puede_procesarse()` |
| RN-12 beneficio por referencia | `beneficio_referencia()` y evento `BeneficioReferenciaOtorgado` |
| RN-16 plazo de 3 días | Specification de plazo |
| RN-17 / RN-22 saldo | Specifications sobre `Dinero` |

Nota: la matriz de trazabilidad del Integrante 1 usa rutas en minúsculas (`src/domain`); en el repositorio
las carpetas son `src/Domain` y `src/Application`, y esas son las rutas reales.
