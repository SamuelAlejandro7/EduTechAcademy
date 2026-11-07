from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

# Inicialización de la API
app = FastAPI(
    title="EduTech Academy API",
    description="Sistema oficial de gestión académica y operativa (PIA UANL FIME).",
    version="2.0.0"
)

# =========================================================
# Manejador global para traducir errores automáticos al español
# =========================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores_limpios = []
    for error in exc.errors():
        ubicacion = error.get("loc", [])
        campo = str(ubicacion[-1]) if ubicacion else "desconocido"
        tipo = error.get("type", "")
        
        # Traducción amigable de los errores de validación más comunes al español
        if "missing" in tipo:
            mensaje = f"El campo '{campo}' es obligatorio y no fue proporcionado."
        elif "type_error" in tipo:
            mensaje = f"El campo '{campo}' tiene un formato o tipo de dato incorrecto."
        else:
            mensaje = error.get("msg", "Error de validación en el campo.")
            
        errores_limpios.append({
            "campo": campo,
            "mensaje": mensaje
        })
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "codigo_error": "ERROR_VALIDACION_DATOS",
            "detalle": "Los datos enviados no cumplen con la estructura requerida.",
            "errores": errores_limpios
        }
    )

# ---------------------------------------------------------
# Esquemas DTO
# ---------------------------------------------------------
class OperacionDTO(BaseModel):
    alumno_id: str = Field(..., example="EDU-C001", description="Identificador único del alumno.")
    programa_id: str = Field(..., example="EDU-P001", description="Identificador del programa formativo.")
    detalles_count: int = Field(..., example=1, description="Número de líneas de detalle en la orden.")
    activo: int = Field(..., example=1, description="Estatus del alumno (1 = Activo, 0 = Inactivo).")
    autorizado: int = Field(..., example=1, description="Autorización administrativa (1 = Sí, 0 = No).")
    monto_total: float = Field(..., example=1800.00, description="Monto total de la orden en MXN.")
    es_preferente: int = Field(..., example=1, description="Indica si cuenta con estatus VIP (1 = Sí, 0 = No).")
    promocion_activa: int = Field(..., example=0, description="Indica si posee otra promoción activa (1 = Sí, 0 = No).")

# ---------------------------------------------------------
# Endpoints de la API REST
# ---------------------------------------------------------

@app.get("/", tags=["Estado del Sistema"], summary="Verificar estado de la API")
def read_root():
    return {
        "status": "online",
        "system": "EduTech Academy Core API",
        "mensaje": "El servicio se encuentra operando correctamente."
    }


@app.post(
    "/api/v1/operaciones/solicitar", 
    status_code=status.HTTP_201_CREATED,
    tags=["Gestión de Operaciones"],
    summary="Registrar solicitud de inscripción (US-01)"
)
def registrar_solicitud(datos: OperacionDTO):
    # Evaluación de la regla RN-11 (puede_procesarse)
    puede_procesarse = (datos.activo == 1) and (datos.detalles_count >= 1) and (datos.autorizado == 1)
    
    if not puede_procesarse:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error de negocio: La operación no cumple con las precondiciones institucionales 'puede_procesarse' (RN-11)."
        )
        
    return {
        "codigo": "OPERACION_SOLICITADA",
        "mensaje": "Operación creada exitosamente en estatus SOLICITADA.",
        "estado_operacion": "SOLICITADA",
        "alumno_id": datos.alumno_id,
        "programa_id": datos.programa_id
    }


@app.post(
    "/api/v1/operaciones/beneficio", 
    status_code=status.HTTP_200_OK,
    tags=["Motor de Reglas y Finanzas"],
    summary="Evaluar concesión de beneficio arancelario VIP (US-22)"
)
def evaluar_beneficio(datos: OperacionDTO):
    # Evaluación de la regla RN-12 (beneficio_referencia)
    aplica_beneficio = (
        datos.es_preferente == 1 and 
        datos.monto_total >= 1500.00 and 
        datos.promocion_activa == 0
    )
    
    monto_final = datos.monto_total * 0.85 if aplica_beneficio else datos.monto_total
    
    return {
        "beneficio_aplicado": aplica_beneficio,
        "monto_original": datos.monto_total,
        "monto_final": round(monto_final, 2),
        "mensaje": "Beneficio arancelario VIP aplicado correctamente (15% de descuento)." if aplica_beneficio else "No aplica descuento VIP (se mantiene importe ordinario)."
    }
