from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field

# Inicialización de la API
app = FastAPI(
    title="🌟 EduTech Academy · Portal de Lógica de Negocio",
    description="Sistema oficial de gestión académica y operativa (PIA UANL FIME).",
    version="2.0.0",
    docs_url=None  # Desactivamos el docs por defecto para personalizarlo
)

# =========================================================
# Swagger UI Personalizado (Diseño moderno, no plano)
# =========================================================
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="EduTech Academy · Documentación Interactiva",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# =========================================================
# Panel Web Visual e Interactivo (/panel)
# =========================================================
@app.get("/panel", response_class=HTMLResponse, tags=["Interfaz Visual"])
async def panel_interactivo():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduTech Academy · Panel Operativo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-6">
        <div class="max-w-4xl mx-auto space-y-6">
            <!-- Header -->
            <header class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                        🎓 EduTech Academy · Panel de Control
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Simulador visual de reglas de negocio y operaciones (PIA FIME)</p>
                </div>
                <a href="/docs" target="_blank" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-indigo-500/20">
                    Ver Swagger UI 🚀
                </a>
            </header>

            <!-- Grid de Herramientas -->
            <div class="grid md:grid-cols-2 gap-6">
                <!-- Tarjeta 1: Solicitar Inscripción -->
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
                    <h2 class="text-lg font-semibold text-blue-400">📋 Registrar Solicitud (RN-11)</h2>
                    <div class="space-y-3 text-sm">
                        <div>
                            <label class="block text-slate-400 mb-1">ID Alumno</label>
                            <input id="sol_alumno" type="text" value="EDU-C001" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-slate-400 mb-1">Estatus Activo (1/0)</label>
                                <input id="sol_activo" type="number" value="1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                            </div>
                            <div>
                                <label class="block text-slate-400 mb-1">Autorizado (1/0)</label>
                                <input id="sol_autorizado" type="number" value="1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                            </div>
                        </div>
                        <div>
                            <label class="block text-slate-400 mb-1">Cantidad de Cursos (Líneas)</label>
                            <input id="sol_detalles" type="number" value="1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        </div>
                        <button onclick="probarSolicitud()" class="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition shadow-lg shadow-blue-500/20">
                            Probar Solicitud
                        </button>
                    </div>
                    <div id="res_solicitud" class="mt-4 p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-slate-300 hidden"></div>
                </div>

                <!-- Tarjeta 2: Beneficio VIP -->
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
                    <h2 class="text-lg font-semibold text-indigo-400">💎 Evaluar Beneficio VIP (RN-12)</h2>
                    <div class="space-y-3 text-sm">
                        <div>
                            <label class="block text-slate-400 mb-1">Monto Total ($ MXN)</label>
                            <input id="ben_monto" type="number" value="1800" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-slate-400 mb-1">¿Es Preferente? (1/0)</label>
                                <input id="ben_preferente" type="number" value="1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                            </div>
                            <div>
                                <label class="block text-slate-400 mb-1">Promoción Activa (1/0)</label>
                                <input id="ben_promo" type="number" value="0" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                            </div>
                        </div>
                        <button onclick="probarBeneficio()" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition shadow-lg shadow-indigo-500/20">
                            Evaluar Beneficio
                        </button>
                    </div>
                    <div id="res_beneficio" class="mt-4 p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-slate-300 hidden"></div>
                </div>
            </div>
        </div>

        <script>
            async function probarSolicitud() {
                const data = {
                    alumno_id: document.getElementById('sol_alumno').value,
                    programa_id: "EDU-P001",
                    detalles_count: parseInt(document.getElementById('sol_detalles').value),
                    activo: parseInt(document.getElementById('sol_activo').value),
                    autorizado: parseInt(document.getElementById('sol_autorizado').value),
                    monto_total: 1500.0,
                    es_preferente: 1,
                    promocion_activa: 0
                };
                const res = await fetch('/api/v1/operaciones/solicitar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const json = await res.json();
                const box = document.getElementById('res_solicitud');
                box.classList.remove('hidden');
                box.innerHTML = `<span class="${res.ok ? 'text-green-400' : 'text-red-400'} font-bold">Status: ${res.status}</span><br>` + JSON.stringify(json, null, 2);
            }

            async function probarBeneficio() {
                const data = {
                    alumno_id: "EDU-C001",
                    programa_id: "EDU-P001",
                    detalles_count: 1,
                    activo: 1,
                    autorizado: 1,
                    monto_total: parseFloat(document.getElementById('ben_monto').value),
                    es_preferente: parseInt(document.getElementById('ben_preferente').value),
                    promocion_activa: parseInt(document.getElementById('ben_promo').value)
                };
                const res = await fetch('/api/v1/operaciones/beneficio', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const json = await res.json();
                const box = document.getElementById('res_beneficio');
                box.classList.remove('hidden');
                box.innerHTML = `<span class="text-green-400 font-bold">Status: ${res.status}</span><br>` + JSON.stringify(json, null, 2);
            }
        </script>
    </body>
    </html>
    """

# =========================================================
# Manejador global para errores de validación en español
# =========================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores_limpios = []
    for error in exc.errors():
        ubicacion = error.get("loc", [])
        campo = str(ubicacion[-1]) if ubicacion else "desconocido"
        tipo = error.get("type", "")
        
        if "missing" in tipo:
            mensaje = f"¡Vaya! El campo '{campo}' es obligatorio y no fue proporcionado."
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
    puede_procesarse = (datos.activo == 1) and (datos.detalles_count >= 1) and (datos.autorizado == 1)
    
    if not puede_procesarse:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error de negocio: La regla 'puede_procesarse' (RN-11) no se cumple con los parámetros actuales."
        )
        
    return {
        "codigo": "OPERACION_SOLICITADA",
        "mensaje": "¡Excelente! Operación creada exitosamente en estatus SOLICITADA. 🎉",
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
        "mensaje": "¡Beneficio arancelario VIP aplicado correctamente (15% de descuento)! ✨" if aplica_beneficio else "No aplica descuento VIP (se mantiene importe ordinario)."
    }
