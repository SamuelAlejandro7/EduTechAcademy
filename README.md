# EduTech Academy — Sistema de Gestión Académica y Operativa
## Producto Integrador de Aprendizaje (PIA)
**Universidad Autónoma de Nuevo León (UANL)**  
**Facultad de Ingeniería Mecánica y Eléctrica (FIME)**  
**Materia:** Componentes de Lógica de Negocio  
**Catedrático:** M.C. Jorge Alejandro Lozano González  
**Equipo:** #15 | **Grupo:** 004  

---

## 👥 Integrantes del Equipo y Asignación de Roles

| Integrante | Matrícula | Rol en el PIA | Enfoque Principal |
| :--- | :---: | :---: | :--- |
| **Samuel Alejandro Casaos Esquivel** | **2226784** | **Persona 1** | **Análisis de Negocio, Documentación y Trazabilidad** (BRD, Glosario, User Stories Gherkin, BPMN y Matriz de Trazabilidad). |
| **Josue Emiliano Diaz García** | **2226766** | **Persona 2** | **Arquitectura de Software, Dominio DDD y Patrones** (Entidades, Value Objects, Patrón Specification, State Machine, ADRs y SOLID). |
| **Maximiliano Romero García** | **2226867** | **Persona 3** | **API REST, Infraestructura, QA, DevOps y Despliegue** (FastAPI, Swagger, Docker Compose, CI/CD GitHub Actions y Suite de Tests $\ge 80\%$). |

---

## 🏛️ Resumen Arquitectónico

El sistema de **EduTech Academy** (Giro: Capacitación Digital) implementa una arquitectura desacoplada por capas basada en los principios de **Domain-Driven Design (DDD)** y **Clean Architecture**:

* **Dominio Puro (`src/Domain/`):**
  * **Agregado `Operacion`:** Raíz de consistencia que resguarda el ciclo de vida y sus líneas formativas.
  * **Patrón Specification:** Reglas de negocio modeladas como objetos combinables (`&`, `|`, `~`):
    * `puede_procesarse()`: $(\text{actor.activo} \land \text{lineas} \ge 1 \land \text{autorizado})$.
    * `beneficio_referencia()`: $(\text{actor.es\_preferente} \land \text{total} \ge \$1,500\text{ MXN} \land \neg \text{promocion\_activa})$.
    * `puede_inscribirse()`: $(\text{recursos\_habilitados} \land \text{cupo\_disponible} \land \text{anticipo} \ge 50\%)$.
  * **Máquina de Estados Finita:** Control transaccional gobernado por tabla de transiciones:  
    $$\text{SOLICITADA} \xrightarrow{\text{aceptar}} \text{ACEPTADA} \xrightarrow{\text{inscribir}} \text{INSCRITA} \xrightarrow{\text{finalizar}} \text{FINALIZADA}$$  
    $$\text{SOLICITADA} \xrightarrow{\text{cancelar}} \text{CANCELADA}$$
  * **Value Objects Inmutables:** `Dinero` (precisión Decimal), `EstadoOperacion`, `Cantidad`, `Porcentaje`.
* **Capa de Aplicación (`src/Application/`):**
  * Servicios de aplicación (`OperacionService`) que orquestan los casos de uso sin absorber reglas de dominio.
* **Capa de API REST (`src/Api/`):**
  * Endpoints construidos en **FastAPI** con documentación interactiva OpenAPI/Swagger y manejo de errores en español con códigos HTTP semánticos (200, 201, 422).
* **Integración Continua (CI/CD):**
  * Pipeline automatizado en **GitHub Actions** (`.github/workflows/ci.yml`) que valida linting y cobertura mínima de pruebas del $80\%$ en cada commit.

---

## 📁 Estructura del Repositorio

```text
EduTechAcademy/
├── .github/workflows/ci.yml      # Pipeline automatizado de CI/CD (GitHub Actions)
├── docker-compose.yml             # Orquestación de contenedores para DB + App + Tests
├── pyproject.toml                 # Configuración de herramientas (pytest, coverage, ruff)
├── README.md                      # Documentación general y guía de ejecución
│
├── Docs/                          # Documentación formal y artefactos
│   ├── BRD.md                     # Business Requirements Document (Persona 1)
│   ├── glossary.md                # Glosario del Lenguaje Ubicuo (Persona 1)
│   ├── user_stories.md            # 22 Historias de Usuario con escenarios Gherkin (Persona 1)
│   ├── traceability_matrix.md     # Matriz de trazabilidad integral end-to-end (Persona 1)
│   ├── bpmn/                      # Modelado de Procesos de Negocio BPMN (Persona 1)
│   │   ├── bpmn_proceso_principal.puml
│   │   ├── bpmn_proceso_principal.mmd
│   │   └── README.md
│   ├── adr/                       # 11 Architecture Decision Records (ADR-001 a ADR-011)
│   ├── arquitectura/              # Guías de integración, modelo de dominio y auditoría SOLID
│   └── resultados_pia/            # Evidencia de los 120 casos de prueba y 20 transiciones
│       ├── resultados_casos.csv
│       └── resultados_transiciones.csv
│
├── Diagramas/                     # Diagramas UML y modelos visuales
│   ├── Fuente/                    # Archivos fuente PlantUML (.puml)
│   └── Exportaciones/             # Exportaciones gráficas en alta resolución (.png, .jpg)
│
├── scripts/                       # Scripts de automatización y verificación
│   └── ejecutar_casos_pia.py      # Ejecutor de homologación de los 140 casos provistos
│
├── src/                           # Código fuente del sistema
│   ├── Api/                       # Endpoints y controladores FastAPI (main.py)
│   ├── Application/               # Servicios de aplicación, DTOs y puertos
│   ├── Domain/                    # Entidades, Value Objects, Specifications y State Machine
│   └── Infrastructure/            # Persistencia, repositorios y cargadores CSV
│
└── tests/                         # Suite de pruebas automatizadas (pytest)
    ├── application/               # Pruebas de casos de uso y servicios
    ├── domain/                    # Pruebas de entidades, specifications y máquina de estados
    ├── test_api.py                # Pruebas de integración de endpoints REST
    └── test_reglas_negocio.py     # Pruebas funcionales basadas en User Stories
```

---

## 🚀 Guía de Instalación y Ejecución Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/SamuelAlejandro7/EduTechAcademy.git
cd EduTechAcademy
```

### 2. Instalar Dependencias
Se recomienda utilizar un entorno virtual con **Python 3.10+**:
```bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn pydantic pytest pytest-cov httpx
```

### 3. Ejecutar la Suite de Pruebas Automatizadas
Para verificar el 100% de las pruebas y la cobertura $\ge 80\%$:
```bash
pytest --cov=src --cov-fail-under=80 -v
```

### 4. Ejecutar la Homologación del Paquete de Pruebas del PIA (140 Casos)
Para procesar `casos_prueba.csv` y `transiciones_prueba.csv` con el motor del dominio:
```bash
python scripts/ejecutar_casos_pia.py
```
Los resultados se actualizan automáticamente en `Docs/resultados_pia/`.

### 5. Iniciar la API REST
```bash
uvicorn src.Api.main:app --reload --port 8000
```
* **Endpoint de bienvenida:** `http://127.0.0.1:8000/`
* **Documentación interactiva Swagger UI:** `http://127.0.0.1:8000/docs`
* **Documentación ReDoc:** `http://127.0.0.1:8000/redoc`

### 6. Ejecución con Docker Compose
```bash
docker-compose up --build
```

---

## 📊 Trazabilidad y Cobertura de Requerimientos

* **Historias de Usuario (Gherkin):** 22 historias documentadas con criterios `Given/When/Then` en [`Docs/user_stories.md`](Docs/user_stories.md).
* **Matriz de Trazabilidad:** Mapeo formal de 12 requerimientos clave contra clases de dominio, endpoints y suites de prueba en [`Docs/traceability_matrix.md`](Docs/traceability_matrix.md).
* **Casos de Prueba del PIA:**
  * 60 pruebas de `validar_operacion` (`puede_procesarse`): 100% evaluadas.
  * 60 pruebas de `evaluar_beneficio` (`beneficio_referencia`): 100% evaluadas.
  * 20 pruebas de transición de máquina de estados: 100% evaluadas (con control estricto de transiciones inválidas).
