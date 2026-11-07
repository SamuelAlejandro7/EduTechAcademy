from fastapi.testclient import TestClient
from src.Api.main import app

# Cliente de pruebas para FastAPI
client = TestClient(app)


def test_verificar_estado_api():
    """Valida que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["mensaje"] == "El servicio se encuentra operando correctamente."


def test_registrar_solicitud_exitosa():
    """Valida la regla RN-11 (puede_procesarse) cuando los datos son válidos."""
    payload = {
        "alumno_id": "EDU-C001",
        "programa_id": "EDU-P001",
        "detalles_count": 1,
        "activo": 1,
        "autorizado": 1,
        "monto_total": 2000.00,
        "es_preferente": 0,
        "promocion_activa": 0
    }
    response = client.post("/api/v1/operaciones/solicitar", json=payload)
    assert response.status_code == 201
    assert response.json()["estado_operacion"] == "SOLICITADA"
    assert response.json()["codigo"] == "OPERACION_SOLICITADA"


def test_registrar_solicitud_rechazada_por_alumno_inactivo():
    """Valida el rechazo de la regla RN-11 cuando el alumno está inactivo."""
    payload = {
        "alumno_id": "EDU-C002",
        "programa_id": "EDU-P001",
        "detalles_count": 1,
        "activo": 0,  # Inactivo
        "autorizado": 1,
        "monto_total": 2000.00,
        "es_preferente": 0,
        "promocion_activa": 0
    }
    response = client.post("/api/v1/operaciones/solicitar", json=payload)
    assert response.status_code == 422
    assert "puede_procesarse" in response.json()["detail"]


def test_evaluar_beneficio_vip_exitoso():
    """Valida la concesión de beneficio VIP (RN-12) con 15% de descuento."""
    payload = {
        "alumno_id": "EDU-C003",
        "programa_id": "EDU-P002",
        "detalles_count": 2,
        "activo": 1,
        "autorizado": 1,
        "monto_total": 2000.00,  # >= 1500
        "es_preferente": 1,      # VIP
        "promocion_activa": 0    # Sin otra promo
    }
    response = client.post("/api/v1/operaciones/beneficio", json=payload)
    assert response.status_code == 200
    assert response.json()["beneficio_aplicado"] is True
    assert response.json()["monto_final"] == 1700.00


def test_evaluar_beneficio_vip_denegado_por_promocion_activa():
    """Valida que la cláusula NOT promocion_activa deniegue la acumulación de promociones."""
    payload = {
        "alumno_id": "EDU-C004",
        "programa_id": "EDU-P002",
        "detalles_count": 1,
        "activo": 1,
        "autorizado": 1,
        "monto_total": 2000.00,
        "es_preferente": 1,
        "promocion_activa": 1  # Ya tiene promoción
    }
    response = client.post("/api/v1/operaciones/beneficio", json=payload)
    assert response.status_code == 200
    assert response.json()["beneficio_aplicado"] is False
    assert response.json()["monto_final"] == 2000.00


def test_error_validacion_espanol():
    """Valida que la omisión de un campo obligatorio devuelva un error traducido al español."""
    payload = {
        "alumno_id": "EDU-C005"
        # Faltan el resto de campos obligatorios
    }
    response = client.post("/api/v1/operaciones/solicitar", json=payload)
    assert response.status_code == 422
    assert response.json()["codigo_error"] == "ERROR_VALIDACION_DATOS"
