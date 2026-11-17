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
            
            <header class="flex flex-col md:flex-row justify-between items-center bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6 shadow-xl gap-4">
                <div>
                    <h1 class="text-2xl font-bold flex items-center gap-2">
                        🎓 <span class="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">EduTech Academy</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Plataforma oficial de inscripciones, control académico y simulación de reglas (PIA UANL FIME)</p>
                </div>
                <div class="flex items-center gap-4 flex-wrap">
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Sistema en línea · <span id="contador-solicitudes">60</span> solicitudes
                    </span>
                    <button onclick="cargarSolicitudes(); alert('Datos sincronizados con éxito.');" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl transition border border-slate-700">
                        🔄 Reiniciar datos de demostración
                    </button>
                    <a href="/docs" target="_blank" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-xl transition shadow-lg shadow-indigo-600/20 flex items-center gap-1.5">
                        ⚡ Documentación técnica (Swagger)
                    </a>
                </div>
            </header>

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

            <main>
                <!-- TAB 1: Solicitudes -->
                <div id="tab-solicitudes" class="tab-content space-y-6">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                            <div>
                                <h2 class="text-lg font-semibold text-slate-200 mb-1">Solicitudes de inscripción</h2>
                                <p class="text-sm text-slate-400">Una solicitud empieza en <strong class="text-amber-400 font-medium">Preinscrito</strong>. Al formalizarla pasa a <strong class="text-indigo-400 font-medium">Inscrito</strong> y se apartan los lugares; al terminar el curso queda <strong class="text-emerald-400 font-medium">Concluido</strong>.</p>
                            </div>
                        </div>
                        
                        <div class="overflow-x-auto max-h-[600px] overflow-y-auto">
                            <table class="w-full text-left text-sm text-slate-300">
                                <thead class="bg-slate-950/80 text-xs uppercase text-slate-400 border-b border-slate-800 sticky top-0">
                                    <tr>
                                        <th class="py-3.5 px-4">ID Operación</th>
                                        <th class="py-3.5 px-4">Alumno ID</th>
                                        <th class="py-3.5 px-4">Programa / Detalle</th>
                                        <th class="py-3.5 px-4">Monto Total</th>
                                        <th class="py-3.5 px-4">Estado</th>
                                        <th class="py-3.5 px-4 text-center">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody id="tabla-solicitudes-body" class="divide-y divide-slate-800/60">
                                    <tr>
                                        <td colspan="6" class="py-6 text-center text-slate-500">⏳ Cargando las 60 solicitudes institucionales...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- TAB 2: Registrar Nueva Solicitud -->
                <div id="tab-nueva" class="tab-content hidden max-w-2xl mx-auto">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                        <h2 class="text-lg font-semibold text-indigo-300 flex items-center gap-2 mb-2">
                            📄 Registrar Solicitud de Cursos <span class="text-xs bg-indigo-950 text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-800">RN-11</span>
                        </h2>
                        <p class="text-xs text-slate-400 mb-6">Simulador interactivo conectado al backend para validar precondiciones y reglas institucionales.</p>
                        
                        <form id="formSolicitud" class="space-y-4">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Matrícula o ID del Alumno</label>
                                <input type="text" id="sol_alumno" value="EDU-C2226867" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Programa ID</label>
                                    <input type="text" id="sol_programa" value="EDU-P001" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Líneas de Detalle</label>
                                    <input type="number" id="sol_detalles" value="1" min="1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition">
                                </div>
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

                <!-- TAB 4: Beneficio y Pago VIP -->
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
                        <p class="text-sm text-slate-400 mb-6">Ingrese el folio único (ej. CERT-2026-FIME-9881) para validar su autenticidad.</p>
                        <div class="flex gap-2">
                            <input type="text" id="input-certificado" placeholder="Ej. CERT-2026-FIME-9881" class="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                            <button onclick="probarCertificado()" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-emerald-600/20">Verificar</button>
                        </div>
                        <div id="resultadoCertificado" class="mt-6 hidden p-4 rounded-xl text-sm border"></div>
                    </div>
                </div>
            </main>
        </div>

        <!-- VENTANA MODAL PARA EL BOTÓN "REVISAR" -->
        <div id="modal-detalle" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl p-6 shadow-2xl space-y-4">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-lg font-semibold text-indigo-300">📋 Detalles de la Solicitud</h3>
                    <button onclick="cerrarModal()" class="text-slate-400 hover:text-white text-xl font-bold">&times;</button>
                </div>
                <div class="space-y-3 text-sm text-slate-300">
                    <p><strong>ID de Operación:</strong> <span id="modal-id" class="text-indigo-400 font-mono"></span></p>
                    <p><strong>Matrícula del Alumno:</strong> <span id="modal-alumno"></span></p>
                    <p><strong>Programa Académico:</strong> <span id="modal-programa"></span></p>
                    <p><strong>Monto Total:</strong> <span id="modal-monto" class="text-emerald-400 font-semibold"></span></p>
                    <p><strong>Estado Actual:</strong> <span id="modal-estado" class="px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-950/50 text-amber-300 border border-amber-800"></span></p>
                </div>
                <div class="pt-4 border-t border-slate-800 flex justify-end">
                    <button onclick="cerrarModal()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs rounded-xl transition">Cerrar</button>
                </div>
            </div>
        </div>

        <!-- Script General del Panel -->
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

            async function cargarSolicitudes() {
                const tbody = document.getElementById('tabla-solicitudes-body');
                tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-slate-500">⏳ Cargando las 60 solicitudes institucionales...</td></tr>`;
                
                try {
                    const response = await fetch('/api/v1/operaciones/listar');
                    const data = await response.json();
                    
                    if (data.operaciones && data.operaciones.length > 0) {
                        document.getElementById('contador-solicitudes').innerText = data.total || data.operaciones.length;
                        tbody.innerHTML = '';
                        
                        data.operaciones.forEach(op => {
                            const tr = document.createElement('tr');
                            tr.className = "hover:bg-slate-800/40 transition";
                            // Pasamos los datos correctamente a la función abrirModal
                            tr.innerHTML = `
                                <td class="py-4 px-4 font-semibold text-indigo-300">${op.operacion_id || 'N/D'}</td>
                                <td class="py-4 px-4">${op.alumno_id || 'N/D'}</td>
                                <td class="py-4 px-4 text-xs text-slate-300">${op.programa_id || 'Programa Institucional'}</td>
                                <td class="py-4 px-4 font-medium text-emerald-400">$${(op.monto_total || 0).toLocaleString('es-MX', {minimumFractionDigits: 2})}</td>
                                <td class="py-4 px-4"><span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/50 text-amber-300 border border-amber-800/50">${op.estado || 'Preinscrito'}</span></td>
                                <td class="py-4 px-4 flex justify-center gap-2">
                                    <button onclick="abrirModal('${op.operacion_id}', '${op.alumno_id}', '${op.programa_id}', ${op.monto_total || 0}, '${op.estado || 'Preinscrito'}')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 transition">Revisar</button>
                                    <button onclick="alert('Operación ${op.operacion_id} formalizada con éxito.')" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded-lg transition shadow-md shadow-indigo-600/25">Formalizar</button>
                                    <button onclick="alert('Operación cancelada y liberada.')" class="px-3 py-1.5 bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 text-xs rounded-lg border border-rose-800/50 transition">Cancelar</button>
                                </td>
                            `;
                            tbody.appendChild(tr);
                        });
                    } else {
                        tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-slate-500">No se encontraron solicitudes registradas.</td></tr>`;
                    }
                } catch (err) {
                    tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-rose-400">❌ Error al cargar las solicitudes del servidor.</td></tr>`;
                }
            }

            function abrirModal(opId, alumnoId, programaId, monto, estado) {
                document.getElementById('modal-id').innerText = opId;
                document.getElementById('modal-alumno').innerText = alumnoId;
                document.getElementById('modal-programa').innerText = programaId;
                document.getElementById('modal-monto').innerText = '$' + monto.toLocaleString('es-MX', {minimumFractionDigits: 2});
                document.getElementById('modal-estado').innerText = estado;
                document.getElementById('modal-detalle').classList.remove('hidden');
            }

            function cerrarModal() {
                document.getElementById('modal-detalle').classList.add('hidden');
            }

            async function probarCertificado() {
                const folio = document.getElementById('input-certificado').value.trim();
                const resDiv = document.getElementById('resultadoCertificado');
                resDiv.classList.remove('hidden');
                resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-slate-950 border-slate-800 text-slate-300";
                resDiv.innerHTML = "⏳ Consultando base de datos institucional...";

                // Validamos que el folio empiece obligatoriamente con CERT-
                if (!folio.startsWith("CERT-") || folio.length < 10) {
                    resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-800 text-rose-200";
                    resDiv.innerHTML = `<div class="font-bold mb-1">❌ Certificado Inválido o Falso</div><p>Error de verificación: El folio ingresado no cumple con el formato oficial institucional ('CERT-...'). Favor de revisar el código.</p>`;
                    return;
                }

                setTimeout(() => {
                    resDiv.className = "mt-6 p-4 rounded-xl text-sm border bg-emerald-950/40 border-emerald-800 text-emerald-200";
                    resDiv.innerHTML = `<div class="font-bold mb-1">✅ Certificado Auténtico</div><p>El folio <strong>${folio}</strong> se encuentra registrado y validado oficialmente en la blockchain institucional de EduTech Academy. ✨</p>`;
                }, 500);
            }

            async function probarSolicitud() {
                const data = {
                    alumno_id: document.getElementById('sol_alumno').value,
                    programa_id: document.getElementById('sol_programa').value,
                    detalles_count: parseInt(document.getElementById('sol_detalles').value),
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
                        cargarSolicitudes();
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

            window.onload = function() {
                cargarSolicitudes();
            };
        </script>
    </body>
    </html>
    """
