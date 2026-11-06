"""Ejecuta los casos del paquete del PIA contra el dominio y genera la evidencia.

Uso:
    python scripts/ejecutar_casos_pia.py RUTA_CSV [RUTA_SALIDA]

Lee actores, catalogo, operaciones, detalle_operaciones, casos_prueba y transiciones_prueba
(CSV UTF-8 con BOM) y escribe resultados_casos.csv y resultados_transiciones.csv.
Usa repositorios en memoria (tests/fakes.py); no modifica los archivos de entrada.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.Application.services import ServicioOperaciones
from src.Domain.entities import Actor, LineaOperacion, Operacion, RecursoFormativo
from src.Domain.errors import ErrorDeDominio
from src.Domain.value_objects import Cantidad, Dinero
from tests.fakes import (
    ActoresEnMemoria,
    OperacionesEnMemoria,
    PublicadorEnMemoria,
    RecursosEnMemoria,
)


def leer(ruta: Path) -> list[dict[str, str]]:
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        return list(csv.DictReader(archivo))


def cargar(carpeta: Path) -> ServicioOperaciones:
    actores = [
        Actor(
            f["actor_id"], f["nombre"], f["es_preferente"] == "1", f["activo"] == "1", f["ciudad"]
        )
        for f in leer(carpeta / "actores.csv")
    ]
    recursos = [
        RecursoFormativo(
            f["recurso_id"],
            f["descripcion"],
            Dinero.de(f["precio_mxn"]),
            int(f["capacidad_o_stock"]),
            f["habilitado"] == "1",
        )
        for f in leer(carpeta / "catalogo.csv")
    ]
    precios = {r.recurso_id: r.precio for r in recursos}
    operaciones = {}
    for f in leer(carpeta / "operaciones.csv"):
        fecha = datetime.fromisoformat(f["fecha_solicitud"][:10]).replace(tzinfo=timezone.utc)
        operaciones[f["operacion_id"]] = Operacion(
            f["operacion_id"],
            f["actor_id"],
            fecha,
            promocion_activa=f["promocion_activa"] == "1",
            autorizado=f["autorizado"] == "1",
            referencia=f["referencia"],
        )
    for f in leer(carpeta / "detalle_operaciones.csv"):
        operaciones[f["operacion_id"]].lineas.append(
            LineaOperacion(f["recurso_id"], precios[f["recurso_id"]], Cantidad(int(f["cantidad"])))
        )
    return ServicioOperaciones(
        ActoresEnMemoria(actores),
        RecursosEnMemoria(recursos),
        OperacionesEnMemoria(list(operaciones.values())),
        PublicadorEnMemoria(),
    )


def escribir(ruta: Path, filas: list[dict[str, str]]) -> None:
    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def main(carpeta: Path, salida: Path) -> None:
    servicio = cargar(carpeta)
    # 1) Casos de reglas (solo lectura: se ejecutan antes de cambiar estados)
    resultados = []
    for caso in leer(carpeta / "casos_prueba.csv"):
        if caso["tipo_prueba"] == "validar_operacion":
            r = servicio.validar_operacion(caso["operacion_id"])
        else:
            r = servicio.evaluar_beneficio(caso["operacion_id"])
        resultados.append(
            {
                "caso_id": caso["caso_id"],
                "operacion_id": caso["operacion_id"],
                "tipo_prueba": caso["tipo_prueba"],
                "regla_a_verificar": caso["regla_a_verificar"],
                "resultado": "CUMPLE" if r.cumple else "NO_CUMPLE",
                "total_mxn": str(r.total),
                "motivos_incumplidos": " | ".join(r.motivos_incumplidos),
            }
        )
    escribir(salida / "resultados_casos.csv", resultados)
    # 2) Transiciones
    transiciones = []
    for caso in leer(carpeta / "transiciones_prueba.csv"):
        try:
            r = servicio.ejecutar_accion_pia(caso["operacion_id"], caso["accion_sugerida"])
            fila = ("EXITO", r.estado_final, " > ".join(r.eventos), "")
        except ErrorDeDominio as error:
            estado = servicio.obtener_operacion(caso["operacion_id"]).estado
            fila = ("ERROR", estado, "", f"{error.codigo}: {error}")
        transiciones.append(
            {
                "caso_id": caso["caso_id"],
                "operacion_id": caso["operacion_id"],
                "accion": caso["accion_sugerida"],
                "estado_inicial": caso["estado_inicial"],
                "resultado": fila[0],
                "estado_final": fila[1],
                "eventos": fila[2],
                "excepcion": fila[3],
            }
        )
    escribir(salida / "resultados_transiciones.csv", transiciones)
    # Resumen
    print("Casos de reglas:", dict(Counter((r["tipo_prueba"], r["resultado"]) for r in resultados)))
    print("Transiciones:", dict(Counter((t["accion"], t["resultado"]) for t in transiciones)))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    destino = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    destino.mkdir(parents=True, exist_ok=True)
    main(Path(sys.argv[1]), destino)
