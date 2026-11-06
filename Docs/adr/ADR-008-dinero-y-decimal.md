# ADR-008: Importes con `Decimal` dentro del Value Object `Dinero`

* **Estado:** Aceptada
* **Fecha:** 2026-11-06
* **Responsable:** Integrante 2

## Contexto
Las instrucciones del paquete piden calcular `total = suma(precio_mxn × cantidad)` con `Decimal`.
Con `float`, sumas como 0.1 + 0.2 no son exactas, y el umbral de 1500 MXN o el anticipo del 50 %
podrían decidirse mal por centavos.

## Decisión
* Todo importe se modela con el Value Object inmutable `Dinero(monto: Decimal, moneda: str)`,
  redondeado a dos decimales (`ROUND_HALF_UP`) y sin valores negativos.
* `Dinero.de()` acepta `int`, `str` y `Decimal`, y **rechaza `float`** y `bool`.
* No se pueden sumar ni comparar monedas distintas.
* La cantidad se modela aparte con `Cantidad` (entero > 0) para que un importe y una cantidad
  no se confundan.
* Los DTOs entregan `Decimal`; la capa API decide cómo serializarlos.

## Alternativas consideradas
1. **`float`.** Descartada por errores de representación binaria.
2. **Enteros en centavos.** Descartada: obliga a convertir en cada borde y es fácil olvidar la escala.

## Consecuencias
* (+) Los límites (1499.99 frente a 1500.00, 399.99 frente a 400.00) se prueban exactamente.
* (−) Integración: el Integrante 3 debe construir `Dinero` desde `str` o `int` al leer CSV y base de
  datos, nunca desde `float`.
