from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

# Inicialización de la API con diseño humanizado y acogedor (Opción 1)
app = FastAPI(
    title="🌟 EduTech Academy · Portal de Lógica de Negocio",
    description="""
    ¡Hola! Te damos la bienvenida al núcleo académico y operativo de **EduTech Academy**. 🎓✨
    
    Esta interfaz te permite explorar y probar de forma interactiva todos los servicios del sistema:
    * 📋 **Gestión de Solicitudes e Inscripciones** (CU-01) con validación automática de reglas de negocio.
    * 📊 **Seguimiento Académico** (CU-02, CU-03) para asistencia y evaluaciones.
    * 📜 **Cierre de Actas y Certificación** (CU-04, CU-05) con verificación pública por código QR.
    
    > *Nota:* Todas nuestras respuestas y mensajes están diseñados para guiarte paso a paso con claridad y transparencia.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =========================================================
# Manejador global para traducir errores automáticos al español (Opción 3)
# =========================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores_limpios = []
    for error in exc.errors():
        ubicacion = error.get("loc", [])
        campo = str(ubicacion[-1]) if ubicacion else "desconocido"
        tipo = error.get("type", "")
        
        # Traducción y humanización de los errores de validación
        if "missing" in tipo:
            mensaje = f"¡Vaya! El campo '{campo}' es obligatorio y no fue proporcionado. Por favor, asegúrate de incluirlo."
        elif "type_error" in tipo:
            mensaje = f"El campo '{campo}' tiene un formato o tipo de dato incorrecto. Por favor, revísalo."
        else:
            mensaje = error.get("msg", "Encontramos un pequeño detalle de validación en este campo.")
            
        errores_limpios.append({
            "campo": campo,
            "mensaje": mensaje
        })
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "codigo_error": "ERROR_VALIDACION_DATOS",
            "detalle": "Los datos enviados no cumplen con la estructura requerida. Te invitamos a corregirlos para continuar.",
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
        "mensaje": "¡Hola! El servicio se encuentra operando correctamente y listo para ayudarte. 🚀"
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
        # Mensajes humanizados y empáticos para errores de negocio (Opción 3)
        if datos.activo != 1:
            detalle_humano = "Lo sentimos mucho, pero no pudimos formalizar esta solicitud porque el estudiante se encuentra actualmente dado de baja. Si consideras que es un error, por favor contacta a Control Escolar. 🛡️"
        elif datos.detalles_count < 1:
            detalle_humano = "¡Hola! Vemos que intentas avanzar con esta solicitud, pero notamos que aún no tiene ningún curso o línea seleccionada. Por favor, asígnale al menos uno antes de continuar. 📚"
        else:
            detalle_humano = "La operación no cuenta con la autorización administrativa requerida para poder proceder en este momento. 🔒"

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detalle_humano
        )
        
    return {
        "codigo": "OPERACION_SOLICITADA",
        "mensaje": "¡Excelente noticia! La operación fue creada exitosamente y se encuentra en estatus SOLICITADA. 🎉",
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
    
    mensaje_amigable = (
        "¡Felicidades! El beneficio arancelario VIP se ha aplicado correctamente (15% de descuento en tu importe total). ✨" 
        if aplica_beneficio 
        else "Evaluamos el beneficio, pero en esta ocasión se mantiene el importe ordinario (recuerda que se requiere estatus preferente, monto mínimo de $1,500 MXN y sin otras promociones activas)."
    )
    
    return {
        "beneficio_aplicado": aplica_beneficio,
        "monto_original": datos.monto_total,
        "monto_final": round(monto_final, 2),
        "mensaje": mensaje_amigable
    }
