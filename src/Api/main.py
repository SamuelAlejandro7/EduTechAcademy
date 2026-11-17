from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="EduTech Academy API",
    description="API moderna con diseño personalizado para gestión y reglas de negocio (PIA FIME).",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Modelos de Pydantic para las Reglas de Negocio
class SolicitudRequest(BaseModel):
    alumno_id: str = Field(..., example="EDU-C001")
    estatus_activo: bool = Field(True, description="¿El alumno está activo?")
    autorizado: bool = Field(True, description="¿La solicitud está autorizada?")
    cantidad_cursos: int = Field(..., ge=1, le=10, description="Número de cursos seleccionados")

class BeneficioVIPRequest(BaseModel):
    monto_total: float = Field(..., gt=0, example=1800.0)
    es_preferente: bool = Field(True, description="¿Es cliente/estudiante preferente?")
    promocion_activa: bool = Field(False, description="¿Tiene otra promoción activa?")


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Bienvenido a EduTech Academy API. Visita /panel para la interfaz visual o /docs para la documentación."}


# Endpoint para Regla de Negocio RN-11 (Simulación lógica)
@app.post("/api/v1/solicitudes/registrar")
def registrar_solicitud(payload: SolicitudRequest):
    if not payload.estatus_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno no se encuentra activo en el sistema."
        )
    if not payload.autorizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La solicitud no cuenta con la autorización requerida."
        )
    
    return {
        "codigo": "OPERACION_SOLICITADA",
        "mensaje": f"¡Excelente! Solicitud creada exitosamente para {payload.cantidad_cursos} curso(s).",
        "estado_operacion": "SOLICITADA",
        "alumno_id": payload.alumno_id,
        "cursos": payload.cantidad_cursos
    }


# Endpoint para Regla de Negocio RN-12 (Beneficio VIP / Descuento)
@app.post("/api/v1/beneficios/evaluar")
def evaluar_beneficio(payload: BeneficioVIPRequest):
    descuento = 0.0
    mensaje = "No aplica beneficio adicional."
    
    if payload.es_preferente and not payload.promocion_activa:
        descuento = 0.15 # 15% de descuento
        mensaje = "¡Beneficio arancelario VIP aplicado correctamente (15% de descuento)! ✨"
    elif payload.promocion_activa:
        mensaje = "Ya cuenta con otra promoción activa; no es acumulable con el beneficio VIP."

    monto_final = payload.monto_total * (1 - descuento)

    return {
        "beneficio_aplicado": descuento > 0,
        "monto_original": payload.monto_total,
        "monto_final": round(monto_final, 2),
        "descuento_porcentaje": int(descuento * 100),
        "mensaje": mensaje
    }


# Interfaz Visual Interactiva Amigable (/panel)
@app.get("/panel", response_class=HTMLResponse, include_in_schema=False)
def panel_control():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduTech Academy · Panel Operativo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen font-sans selection:bg-indigo-500 selection:text-white">
        <div class="max-w-7xl mx-auto px-4 py-8">
            
            <!-- Encabezado -->
            <header class="flex flex-col md:flex-row justify-between items-center bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8 shadow-xl">
                <div>
                    <h1 class="text-2xl font-bold flex items-center gap-2">
                        🎓 <span class="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">EduTech Academy · Panel de Control</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Simulador visual intuitivo para validación de reglas de negocio (PIA FIME)</p>
                </div>
                <div class="mt-4 md:mt-0 flex gap-3">
                    <a href="/docs" target="_blank" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-indigo-600/20 flex items-center gap-2">
                        Ver Swagger UI 🚀
                    </a>
                </div>
            </header>

            <!-- Grid de Módulos -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                <!-- Módulo 1: Registrar Solicitud (RN-11) -->
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
                    <div>
                        <h2 class="text-lg font-semibold text-indigo-300 flex items-center gap-2 mb-4">
                            📄 Registrar Solicitud de Cursos <span class="text-xs bg-indigo-950 text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-800">RN-11</span>
                        </h2>
                        
                        <form id="formSolicitud" class="space-y-4">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Matrícula o ID del Alumno</label>
                                <input type="text" id="sol_alumno" value="EDU-C2226867" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Estatus del Alumno</label>
                                    <select id="sol_activo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                                        <option value="true">Activo</option>
                                        <option value="false">Inactivo</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Autorización Académica</label>
                                    <select id="sol_autorizado" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                                        <option value="true">Autorizado</option>
                                        <option value="false">No Autorizado</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Cantidad de Cursos (1 a 10)</label>
                                <input type="number" id="sol_cursos" min="1" max="10" value="4" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                            </div>

                            <button type="button" onclick="probarSolicitud()" class="w-full py-3 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium rounded-xl transition shadow-lg shadow-indigo-600/20">
                                Ejecutar Solicitud
                            </button>
                        </form>
                    </div>

                    <!-- Resultado Visual Dinámico -->
                    <div id="resultadoSolicitud" class="mt-6 hidden p-4 rounded-xl text-sm border"></div>
                </div>

                <!-- Módulo 2: Beneficio VIP (RN-12) -->
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
                    <div>
                        <h2 class="text-lg font-semibold text-cyan-300 flex items-center gap-2 mb-4">
                            💎 Evaluar Beneficio Arancelario <span class="text-xs bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-800">RN-12</span>
                        </h2>
                        
                        <form id="formBeneficio" class="space-y-4">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total a Pagar ($ MXN)</label>
                                <input type="number" id="ben_monto" value="2500" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">¿Es Estudiante Preferente?</label>
                                    <select id="ben_preferente" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                                        <option value="true">Sí (Aplica VIP)</option>
                                        <option value="false">No</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">¿Otra Promoción Activa?</label>
                                    <select id="ben_promo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                                        <option value="false">No</option>
                                        <option value="true">Sí</option>
                                    </select>
                                </div>
                            </div>

                            <button type="button" onclick="probarBeneficio()" class="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-xl transition shadow-lg shadow-cyan-600/20">
                                Calcular Beneficio
                            </button>
                        </form>
                    </div>

                    <!-- Resultado Visual Dinámico -->
                    <div id="resultadoBeneficio" class="mt-6 hidden p-4 rounded-xl text-sm border"></div>
                </div>

            </div>
        </div>

        <!-- Script de interacción amigable -->
        <script>
            async function probarSolicitud() {
                const data = {
                    alumno_id: document.getElementById('sol_alumno').value,
                    estatus_activo: document.getElementById('sol_activo').value === 'true',
                    autorizado: document.getElementById('sol_autorizado').value === 'true',
                    cantidad_cursos: parseInt(document.getElementById('sol_cursos').value)
                };

                const resDiv = document.getElementById('resultadoSolicitud');
                resDiv.classList.remove('hidden');
                resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-slate-950 border-slate-800 text-slate-300";
                resDiv.innerHTML = "⏳ Procesando solicitud...";

                try {
                    const response = await fetch('/api/v1/solicitudes/registrar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const json = await response.json();

                    if (response.ok) {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-emerald-950/40 border-emerald-800 text-emerald-200";
                        resDiv.innerHTML = `
                            <div class="font-bold flex items-center gap-2 mb-1">✅ Solicitud Aprobada (Código 201)</div>
                            <p class="text-emerald-300">${json.mensaje}</p>
                            <div class="text-xs text-emerald-400/80 mt-2">Alumno: ${json.alumno_id} | Cursos: ${json.cursos}</div>
                        `;
                    } else {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                        resDiv.innerHTML = `
                            <div class="font-bold flex items-center gap-2 mb-1">❌ Solicitud Rechazada</div>
                            <p>${json.detail}</p>
                        `;
                    }
                } catch (err) {
                    resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                    resDiv.innerHTML = "❌ Error de conexión con el servidor.";
                }
            }

            async function probarBeneficio() {
                const data = {
                    monto_total: parseFloat(document.getElementById('ben_monto').value),
                    es_preferente: document.getElementById('ben_preferente').value === 'true',
                    promocion_activa: document.getElementById('ben_promo').value === 'true'
                };

                const resDiv = document.getElementById('resultadoBeneficio');
                resDiv.classList.remove('hidden');
                resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-slate-950 border-slate-800 text-slate-300";
                resDiv.innerHTML = "⏳ Evaluando beneficio...";

                try {
                    const response = await fetch('/api/v1/beneficios/evaluar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const json = await response.json();

                    if (response.ok) {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-cyan-950/40 border-cyan-800 text-cyan-200";
                        resDiv.innerHTML = `
                            <div class="font-bold flex items-center gap-2 mb-1">💎 Evaluación Exitosa (Código 200)</div>
                            <p class="text-cyan-200 font-medium">${json.mensaje}</p>
                            <div class="mt-3 pt-3 border-t border-cyan-900/50 grid grid-cols-2 text-xs">
                                <div>Monto Original: <span class="font-semibold">$${json.monto_original} MXN</span></div>
                                <div>Monto Final: <span class="font-semibold text-emerald-400">$${json.monto_final} MXN</span></div>
                            </div>
                        `;
                    } else {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                        resDiv.innerHTML = `<div class="font-bold">❌ Error al evaluar beneficio.</div>`;
                    }
                } catch (err) {
                    resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                    resDiv.innerHTML = "❌ Error de conexión con el servidor.";
                }
            }
        </script>
    </body>
    </html>
    """
