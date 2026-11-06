# ADR-004: Arquitectura por capas con puertos (hexagonal) y DDD

* **Estado:** Aceptada
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
El PIA exige reglas de negocio verificables con pruebas automatizadas (cobertura ≥ 80 %), una API
REST, persistencia y despliegue. El equipo trabaja en paralelo: el Integrante 3 construye API,
infraestructura y pruebas mientras el dominio todavía se está definiendo. Hace falta una
estructura que permita probar las reglas sin base de datos ni servidor web y que deje claro qué
carpeta pertenece a quién.

## Decisión
Se adopta Domain-Driven Design con una arquitectura por capas y puertos (hexagonal):

| Capa | Carpeta | Responsabilidad | Puede importar |
|---|---|---|---|
| Dominio | `src/Domain/` | Entidades, Value Objects, agregados, Specifications, máquina de estados, eventos y *puertos* de repositorio | Solo la librería estándar |
| Aplicación | `src/Application/` | Casos de uso, DTOs, puertos de salida (publicador de eventos) | Dominio |
| Infraestructura | `src/Infrastructure/` (Integrante 3) | Implementaciones de repositorios (CSV / SQL) y adaptadores | Dominio y aplicación |
| API | `src/api/` (Integrante 3) | Controladores REST | Aplicación |

La dependencia siempre apunta hacia el dominio. Las interfaces de repositorio viven en el dominio
(`src/Domain/repositories.py`) y las implementa infraestructura (inversión de dependencias).

## Alternativas consideradas
1. **MVC con modelos anémicos y lógica en controladores.** Descartada: las reglas quedarían
   mezcladas con HTTP y no se podrían probar de forma aislada.
2. **Dominio dependiente de SQLAlchemy (modelos ORM como entidades).** Descartada: acopla las
   reglas a la base de datos y complica las pruebas unitarias.

## Consecuencias
* (+) El dominio y la aplicación se prueban con repositorios en memoria (`tests/fakes.py`), sin
  base de datos. En esta entrega las 99 pruebas corren en menos de un segundo.
* (+) El Integrante 3 puede cambiar CSV por SQL sin tocar reglas.
* (−) Hay que escribir un traductor entre filas de base de datos y entidades en infraestructura.
* Se verificó que `src/Domain` no importa nada de `src/Application`, `src/Infrastructure` ni `src/api`.
