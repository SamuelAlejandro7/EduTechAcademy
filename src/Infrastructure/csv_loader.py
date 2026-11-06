import csv
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any


class CSVDataLoader:
    """
    Capa de Infraestructura: Cargador y procesador de archivos CSV 
    para la persistencia inicial y cálculo de operaciones del PIA.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def _read_csv(self, filename: str) -> List[Dict[str, Any]]:
        """Lee un archivo CSV manejando la codificación UTF-8 con BOM."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")

        with open(filepath, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            return [row for row in reader]

    def load_actores((self) -> List[Dict[str, Any]]:
        """Carga la lista de 40 actores."""
        return self._read_csv("actores.csv")

    def load_catalogo(self) -> List[Dict[str, Any]]:
        """Carga el catálogo de 20 recursos formativos."""
        catalogo = self._read_csv("catalogo.csv")
        # Convertir precios a Decimal
        for item in catalogo:
            if "precio_mxn" in item:
                item["precio_mxn"] = Decimal(str(item["precio_mxn"]))
        return catalogo

    def load_operaciones(self) -> List[Dict[str, Any]]:
        """Carga las 60 operaciones iniciales en estado SOLICITADA."""
        return self._read_csv("operaciones.csv")

    def load_detalle_operaciones(self) -> List[Dict[str, Any]]:
        """Carga el detalle de las operaciones."""
        detalles = self._read_csv("detalle_operaciones.csv")
        for item in detalles:
            if "precio_mxn" in item:
                item["precio_mxn"] = Decimal(str(item["precio_mxn"]))
            if "cantidad" in item:
                item["cantidad"] = int(item["cantidad"])
        return detalles

    def calcular_totales_operaciones(self) -> Dict[str, Decimal]:
        """
        Calcula el total de cada operación acumulando (precio_mxn * cantidad)
        utilizando precisión Decimal conforme a las reglas del PIA.
        """
        detalles = self.load_detalle_operaciones()
        totales: Dict[str, Decimal] = {}

        for fila in detalles:
            op_id = fila["operacion_id"]
            precio = fila["precio_mxn"]
            cantidad = Decimal(fila["cantidad"])

            subtotal = precio * cantidad

            if op_id in totales:
                totales[op_id] += subtotal
            else:
                totales[op_id] = subtotal

        return totales


# Ejemplo de uso rápido / prueba de infraestructura
if __name__ == "__main__":
    loader = CSVDataLoader(data_dir="01_Alumno/datos")
    try:
        actores = loader.load_actores()
        catalogo = loader.load_catalogo()
        operaciones = loader.load_operaciones()
        totales = loader.calcular_totales_operaciones()

        print(f"✅ Actores cargados: {len(actores)}")
        print(f"✅ Recursos en catálogo: {len(catalogo)}")
        print(f"✅ Operaciones cargadas: {len(operaciones)}")
        print(f"✅ Totales calculados para {len(totales)} operaciones.")
    except Exception as e:
        print(f"⚠️ Nota: Asegúrate de colocar los archivos CSV en la carpeta indicada. Detalle: {e}")
