from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

app = FastAPI(
    title="EduTech Academy API",
    description="API moderna con diseño personalizado para gestión y reglas de negocio (PIA FIME).",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "codigo_error": "ERROR_VALIDACION_DATOS",
            "detail": str(exc.errors())
        }
    )

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
    return {
        "status": "online",
        "mensaje": "El servicio se encuentra operando correctamente."
    }


@app.post("/api/v1/operaciones/solicitar", status_code=status.HTTP_201_CREATED)
def registrar_solicitud(payload: SolicitudRequest):
    if payload.activo == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error en la regla puede_procesarse: El alumno no se encuentra activo."
        )
    if payload.autorizado == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error en la regla puede_procesarse: La solicitud no está autorizada."
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


# Interfaz Visual Interactiva con el Menú Completo y Estilo Moderno (/panel)
@app.get("/panel", response_class=HTMLResponse, include_in_schema=False)
def panel_control():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduTech Academy · Panel Operativo Avanzado</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen font-sans selection:bg-indigo-500 selection:text-white">
        <div class="max-w-7xl mx-auto px-4 py-8">
            
            <!-- Encabezado Principal -->
            <header class="flex flex-col md:flex-row justify-between items-center bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6 shadow-xl gap-4">
                <div>
                    <h1 class="text-2xl font-bold flex items-center gap-2">
                        🎓 <span class="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">EduTech Academy</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Plataforma de inscripciones, control académico y simulación de reglas de negocio</p>
                </div>
                <div class="flex items-center gap-4 flex-wrap">
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Sistema en línea · 60 solicitudes
                    </span>
                    <button onclick="alert('Datos de demostración restablecidos con éxito.');" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl transition border border-slate-700">
                        🔄 Reiniciar datos de demostración
                    </button>
                    <a href="/docs" target="_blank" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-xl transition shadow-lg shadow-indigo-600/20 flex items-center gap-1.5">
                        ⚡ Documentación técnica (Swagger)
                    </a>
                </div>
            </header>

            <!-- Menú de Pestañas Estilizado -->
            <nav class="flex border-b border-slate-800 mb-8 overflow-x-auto gap-2">
                <button onclick="cambiarTab('solicitudes')" id="btn-solicitudes" class="tab-btn px-5 py-3 text-sm font-semibold border-b-2 border-indigo-500 text-indigo-400 flex items-center gap-2 transition whitespace-nowrap">
                    📋 Solicitudes de Inscripción
                </button>
                <button onclick="cambiarTab('nueva')" id="btn-nueva" class="tab-btn px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 transition whitespace-nowrap">
                    ✨ Registrar Nueva Solicitud (RN-11)
                </button>
                <button onclick="cambiarTab('cursos')" id="btn-cursos" class="tab-btn px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 transition whitespace-nowrap">
                    📚 Cursos y Cupos
                </button>
                <button onclick="cambiarTab('pago')" id="btn-pago" class="tab-btn px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 transition whitespace-nowrap">
                    💎 Beneficio y Pago VIP (RN-12)
                </button>
                <button onclick="cambiarTab('verificar')" id="btn-verificar" class="tab-btn px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 transition whitespace-nowrap">
                    🔍 Verificar Certificado
                </button>
            </nav>

            <!-- Contenido de las Pestañas -->
            <main>
                <!-- TAB 1: Solicitudes (Tabla completa inicial) -->
                <div id="tab-solicitudes" class="tab-content space-y-6">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                        <h2 class="text-lg font-semibold text-slate-200 mb-2">Solicitudes de inscripción</h2>
                        <p class="text-sm text-slate-400 mb-6">Una solicitud empieza en <strong class="text-amber-400 font-medium">Preinscrito</strong>. Al formalizarla pasa a <strong class="text-indigo-400 font-medium">Inscrito</strong> y se apartan los lugares; al terminar el curso queda <strong class="text-emerald-400 font-medium">Concluido</strong>. Si se cancela antes de formalizarla queda <strong class="text-rose-400 font-medium">Liberada</strong>.</p>
                        
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-sm text-slate-300">
                                <thead class="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
                                    <tr>
                                        <th class="py-3.5 px-4">Solicitud</th>
                                        <th class="py-3.5 px-4">Estudiante</th>
                                        <th class="py-3.5 px-4">Cursos (Lugares)</th>
                                        <th class="py-3.5 px-4">Total</th>
                                        <th class="py-3.5 px-4">Estado</th>
                                        <th class="py-3.5 px-4 text-center">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-800/60">
                                    <tr class="hover:bg-slate-800/40 transition">
                                        <td class="py-4 px-4 font-semibold text-indigo-300">EDU-0001</td>
                                        <td class="py-4 px-4">Alumno 23<br><span class="text-xs text-slate-500">EDU-C023</span></td>
                                        <td class="py-4 px-4 text-xs text-slate-300">EDU-P009 (3)<br>EDU-P014 (4)</td>
                                        <td class="py-4 px-4 font-medium text-emerald-400">$9,358.00</td>
                                        <td class="py-4 px-4"><span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/50 text-amber-300 border border-amber-800/50">Preinscrito</span></td>
                                        <td class="py-4 px-4 flex justify-center gap-2">
                                            <button onclick="alert('Revisando detalles de la solicitud EDU-0001')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 transition">Revisar</button>
                                            <button onclick="alert('Solicitud formalizada exitosamente.')" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded-lg transition shadow-md shadow-indigo-600/25">Formalizar</button>
                                            <button onclick="alert('Solicitud cancelada y liberada.')" class="px-3 py-1.5 bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 text-xs rounded-lg border border-rose-800/50 transition">Cancelar</button>
                                        </td>
                                    </tr>
                                    <tr class="hover:bg-slate-800/40 transition">
                                        <td class="py-4 px-4 font-semibold text-indigo-300">EDU-0002</td>
                                        <td class="py-4 px-4">Alumno 30<br><span class="text-xs text-slate-500">EDU-C030</span></td>
                                        <td class="py-4 px-4 text-xs text-slate-300">EDU-P012 (4)<br>EDU-P017 (1)</td>
                                        <td class="py-4 px-4 font-medium text-emerald-400">$8,364.00</td>
                                        <td class="py-4 px-4"><span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/50 text-amber-300 border border-amber-800/50">Preinscrito</span></td>
                                        <td class="py-4 px-4 flex justify-center gap-2">
                                            <button onclick="alert('Revisando detalles de la solicitud EDU-0002')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 transition">Revisar</button>
                                            <button onclick="alert('Solicitud formalizada exitosamente.')" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded-lg transition shadow-md shadow-indigo-600/25">Formalizar</button>
                                            <button onclick="alert('Solicitud cancelada y liberada.')" class="px-3 py-1.5 bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 text-xs rounded-lg border border-rose-800/50 transition">Cancelar</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- TAB 2: Registrar Nueva Solicitud (RN-11 Interactiva) -->
                <div id="tab-nueva" class="tab-content hidden max-w-2xl mx-auto">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                        <h2 class="text-lg font-semibold text-indigo-300 flex items-center gap-2 mb-2">
                            📄 Registrar Solicitud de Cursos <span class="text-xs bg-indigo-950 text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-800">RN-11</span>
                        </h2>
                        <p class="text-xs text-slate-400 mb-6">Simulador interactivo conectado al backend para validar las reglas de negocio en tiempo real.</p>
                        
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
                                Ejecutar y Validar Solicitud
                            </button>
                        </form>
                        <div id="resultadoSolicitud" class="mt-6 hidden p-4 rounded-xl text-sm border"></div>
                    </div>
                </div>

                <!-- TAB 3: Cursos y Cupos -->
                <div id="tab-cursos" class="tab-content hidden space-y-6">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                        <h2 class="text-lg font-semibold text-cyan-300 mb-2">📚 Catálogo de Cursos y Control de Cupos</h2>
                        <p class="text-sm text-slate-400 mb-4">Gestión de disponibilidad y cupos máximos por programa académico.</p>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                                <h3 class="font-semibold text-indigo-300">EDU-P001 · Programación Avanzada</h3>
                                <p class="text-xs text-slate-400 mt-1">Cupo máximo: 30 alumnos</p>
                                <span class="inline-block mt-3 px-2.5 py-1 text-xs bg-emerald-950 text-emerald-400 rounded-full border border-emerald-800">Disponibles: 12 lugares</span>
                            </div>
                            <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                                <h3 class="font-semibold text-indigo-300">EDU-P002 · Arquitectura de Software</h3>
                                <p class="text-xs text-slate-400 mt-1">Cupo máximo: 25 alumnos</p>
                                <span class="inline-block mt-3 px-2.5 py-1 text-xs bg-amber-950 text-amber-400 rounded-full border border-amber-800">Cupo casi lleno (3 lugares)</span>
                            </div>
                            <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                                <h3 class="font-semibold text-indigo-300">EDU-P003 · Inteligencia Artificial</h3>
                                <p class="text-xs text-slate-400 mt-1">Cupo máximo: 30 alumnos</p>
                                <span class="inline-block mt-3 px-2.5 py-1 text-xs bg-emerald-950 text-emerald-400 rounded-full border border-emerald-800">Disponibles: 18 lugares</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- TAB 4: Inscripción y Pago (RN-12 Interactiva) -->
                <div id="tab-pago" class="tab-content hidden max-w-2xl mx-auto">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                        <h2 class="text-lg font-semibold text-cyan-300 flex items-center gap-2 mb-2">
                            💎 Evaluar Beneficio Arancelario <span class="text-xs bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-800">RN-12</span>
                        </h2>
                        <p class="text-xs text-slate-400 mb-6">Simulador de descuentos por categoría preferente y exclusión de promociones.</p>
                        
                        <form id="formBeneficio" class="space-y-4">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total a Pagar ($ MXN)</label>
                                <input type="number" id="ben_monto" value="2000" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">¿Es Estudiante Preferente?</label>
                                    <select id="ben_preferente" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                                        <option value="1">Sí (Aplica VIP 15%)</option>
                                        <option value="0">No</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">¿Otra Promoción Activa?</label>
                                    <select id="ben_promo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 transition">
                                        <option value="0">No</option>
                                        <option value="1">Sí (No acumulable)</option>
                                    </select>
                                </div>
                            </div>
                            <button type="button" onclick="probarBeneficio()" class="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-xl transition shadow-lg shadow-cyan-600/20">
                                Calcular Beneficio y Pago Final
                            </button>
                        </form>
                        <div id="resultadoBeneficio" class="mt-6 hidden p-4 rounded-xl text-sm border"></div>
                    </div>
                </div>

                <!-- TAB 5: Verificar Certificado -->
                <div id="tab-verificar" class="tab-content hidden max-w-xl mx-auto">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-center">
                        <h2 class="text-lg font-semibold text-emerald-300 mb-2">🔍 Verificación de Certificados Digitales</h2>
                        <p class="text-sm text-slate-400 mb-6">Ingrese el folio único de certificación para validar su autenticidad en la blockchain o base de datos institucional.</p>
                        <div class="flex gap-2">
                            <input type="text" placeholder="Ej. CERT-2026-FIME-9881" class="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                            <button onclick="alert('Certificado verificado: Válido y emitido por EduTech Academy.')" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-emerald-600/20">Verificar</button>
                        </div>
                    </div>
                </div>
            </main>
        </div>

        <!-- Script de Pestañas y Conexión de API -->
        <script>
            function cambiarTab(tabId) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                document.getElementById('tab-' + tabId).classList.remove('hidden');

                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('border-indigo-500', 'text-indigo-400', 'font-semibold');
                    btn.classList.add('border-transparent', 'text-slate-400', 'font-medium');
                });
                const activeBtn = document.getElementById('btn-' + tabId);
                activeBtn.classList.remove('border-transparent', 'text-slate-400', 'font-medium');
                activeBtn.classList.add('border-indigo-500', 'text-indigo-400', 'font-semibold');
            }

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
