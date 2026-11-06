# Arquitectura, dominio DDD y patrones (Integrante 2)

Documentación de la capa de dominio y aplicación de EduTech Academy.

| Documento | Contenido |
|---|---|
| [modelo_dominio.md](modelo_dominio.md) | Entidades, Value Objects, agregado, eventos, Specification y máquina de estados, con diagramas |
| [SOLID.md](SOLID.md) | Cómo se aplica cada principio SOLID en el código |
| [guia_integracion.md](guia_integracion.md) | Cómo usan el dominio los Integrantes 1 y 3, resultados de los casos y correspondencia con las reglas RN |

## ADR (carpeta [`../adr`](../adr))

Los ADR-001 a ADR-003 son del Integrante 1; los siguientes son de esta parte.

* [ADR-004 Arquitectura por capas](../adr/ADR-004-arquitectura-por-capas.md)
* [ADR-005 Agregado Operacion](../adr/ADR-005-agregado-operacion.md)
* [ADR-006 Patrón Specification](../adr/ADR-006-patron-specification.md)
* [ADR-007 Máquina de estados](../adr/ADR-007-maquina-de-estados.md)
* [ADR-008 Dinero y Decimal](../adr/ADR-008-dinero-y-decimal.md)
* [ADR-009 Eventos de dominio](../adr/ADR-009-eventos-de-dominio.md)
* [ADR-010 Errores y contrato API](../adr/ADR-010-errores-y-contrato-api.md)
* [ADR-011 Paquete de pruebas vs BRD](../adr/ADR-011-paquete-de-pruebas-vs-brd.md)

## Código y pruebas

* `src/Domain/` y `src/Application/` (módulos Python `.py`); `tests/` con 99 pruebas y 100 % de cobertura.
* Diagramas: fuentes `.puml` en `Diagramas/Fuente`, imágenes en `Diagramas/Exportaciones`.
