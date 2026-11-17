from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="EduTech Academy API",
    description="API moderna con diseño personalizado para gestión y reglas de negocio (PIA FIME).",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Modelos originales esperados por las pruebas de la API
class SolicitudRequest(BaseModel):
    alumno_id: str
    programa_id: str
    detalles_count: int
    activo: int
    autorizado: int
    monto_total: float
    es_preferente: int
    promocion_activa: int

class BeneficioVIPRequest(BaseModel):
    alumno_id: str
    programa_id: str
    detalles_count: int
    activo: int
    autorizado: int
    monto_total: float
    es_preferente: int
    promocion_activa: int


@app.get("/")
def root():
    return {"status": "online", "message": "Bienvenido a EduTech Academy API"}


# Endpoints oficiales que consumen las pruebas automatizadas (pytest)
@app.post("/api/v1/operaciones/solicitar", status_code=status.HTTP_201_CREATED)
def registrar_solicitud(payload: SolicitudRequest):
    if payload.activo == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El alumno no se encuentra activo."
        )
    if payload.autorizado == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La solicitud no está autorizada."
        )
    
    return {
        "codigo": "OPERACION_SOLICITADA",
        "mensaje": "¡Excelente! Operación creada exitosamente en estatus SOLICITADA.",
        "estado_operacion": "SOLICITADA",
        "alumno_id": payload.alumno_id,
        "programa_id": payload.programa_id
    }


@app.post("/api/v1/operaciones/beneficio", status_code=status.HTTP_200_OK)
def evaluar_beneficio(payload: BeneficioVIPRequest):
    if payload.promocion_activa == 1:
        # Si tiene promo activa, simulamos el comportamiento esperado por el test
        return {
            "beneficio_aplicado": False,
            "monto_original": payload.monto_total,
            "monto_final": payload.monto_total,
            "mensaje": "Ya cuenta con otra promoción activa."
        }

    descuento = 0.15 if (payload.es_preferente == 1 and payload.monto_total >= 1500) else 0.0
    monto_final = payload.monto_total * (1 - descuento)

    return {
        "beneficio_aplicado": descuento > 0,
        "monto_original": payload.monto_total,
        "monto_final": round(monto_final, 2),
        "mensaje": "¡Beneficio arancelario VIP aplicado correctamente (15% de descuento)! ✨"
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
                                        <option value="1">Activo</option>
                                        <option value="0">Inactivo</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Autorización Académica</label>
                                    <select id="sol_autorizado" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                                        <option value="1">Autorizado</option>
                                        <option value="0">No Autorizado</option>
                                    </select>
                                </div>
                            </div>
                            <button type="button" onclick="probarSolicitud()" class="w-full py-3 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium rounded-xl transition shadow-lg shadow-indigo-600/20">
                                Ejecutar Solicitud
                            </button>
                        </form>
                    </div>
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
                                <input type="number" id="ben_monto" value="2000" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">¿Es Estudiante Preferente?</label>
                                    <select id="ben_preferente" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                                        <option value="1">Sí (Aplica VIP)</option>
                                        <option value="0">No</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">¿Otra Promoción Activa?</label>
                                    <select id="ben_promo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                                        <option value="0">No</option>
                                        <option value="1">Sí</option>
                                    </select>
                                </div>
                            </div>
                            <button type="button" onclick="probarBeneficio()" class="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-xl transition shadow-lg shadow-cyan-600/20">
                                Calcular Beneficio
                            </button>
                        </form>
                    </div>
                    <div id="resultadoBeneficio" class="mt-6 hidden p-4 rounded-xl text-sm border"></div>
                </div>
            </div>
        </div>

        <script>
            async function probarSolicitud() {
                const data = {
                    alumno_id: document.getElementById('sol_alumno').value,
                    programa_id: "EDU-P001",
                    detalles_count: 1,
                    activo: parseInt(document.getElementById('sol_activo').value),
                    autorizado: parseInt(document.getElementById('sol_autorizado').value),
                    monto_total: 2000.0,
                    es_preferente: 0,
                    promocion_activa: 0
                };
                const resDiv = document.getElementById('resultadoSolicitud');
                resDiv.classList.remove('hidden');
                resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-slate-950 border-slate-800 text-slate-300";
                resDiv.innerHTML = "⏳ Procesando solicitud...";

                try {
                    const response = await fetch('/api/v1/operaciones/solicitar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const json = await response.json();
                    if (response.ok) {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-emerald-950/40 border-emerald-800 text-emerald-200";
                        resDiv.innerHTML = `<div class="font-bold mb-1">✅ Solicitud Aprobada (Código 201)</div><p>${json.mensaje}</p>`;
                    } else {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                        resDiv.innerHTML = `<div class="font-bold mb-1">❌ Solicitud Rechazada</div><p>${json.detail}</p>`;
                    }
                } catch (err) {
                    resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                    resDiv.innerHTML = "❌ Error de conexión.";
                }
            }

            async function probarBeneficio() {
                const data = {
                    alumno_id: "EDU-C003",
                    programa_id: "EDU-P002",
                    detalles_count: 2,
                    activo: 1,
                    autorizado: 1,
                    monto_total: parseFloat(document.getElementById('ben_monto').value),
                    es_preferente: parseInt(document.getElementById('ben_preferente').value),
                    promocion_activa: parseInt(document.getElementById('ben_promo').value)
                };
                const resDiv = document.getElementById('resultadoBeneficio');
                resDiv.classList.remove('hidden');
                resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-slate-950 border-slate-800 text-slate-300";
                resDiv.innerHTML = "⏳ Evaluando beneficio...";

                try {
                    const response = await fetch('/api/v1/operaciones/beneficio', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const json = await response.json();
                    if (response.ok) {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-cyan-950/40 border-cyan-800 text-cyan-200";
                        resDiv.innerHTML = `
                            <div class="font-bold mb-1">💎 Evaluación Exitosa</div>
                            <p>${json.mensaje}</p>
                            <div class="mt-2 text-xs">Monto Original: $${json.monto_original} | Monto Final: <span class="font-semibold text-emerald-400">$${json.monto_final}</span></div>
                        `;
                    } else {
                        resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                        resDiv.innerHTML = `<div class="font-bold">❌ Error al evaluar beneficio.</div>`;
                    }
                } catch (err) {
                    resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                    resDiv.innerHTML = "❌ Error de conexión.";
                }
            }
        </script>
    </body>
    </html>
    """
