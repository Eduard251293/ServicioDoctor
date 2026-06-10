# ============================================================
# main.py - SERVICIO DOCTORES
# Ubicación: EcoSistemaSalud/ServicioDoctores/main.py
# Solo arranca el servidor y registra los endpoints
# Cada endpoint vive en su propio archivo en Endpoints/
# Ejecutar: python main.py
# Documentación: http://localhost:8001/docs
# Panel visual: http://localhost:8001/panel
# ============================================================

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Agregar EcoSistemaSalud al path para importar database.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar cada endpoint por separado
from Endpoints.post_doctor_diagnostico  import router as router_diagnostico
from Endpoints.post_doctor_orden_medica import router as router_orden
from Endpoints.post_doctor_receta       import router as router_receta
from Endpoints.get_pacientes_atendidos  import router as router_pacientes
from Endpoints.get_consulta_paciente    import router as router_consulta
from Endpoints.get_recetas_paciente     import router as router_recetas

# ── Inicializar FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title       = "ServicioDoctores - EcoSistemaSalud",
    description = """
    Microservicio de Doctores del Ecosistema de Salud Conectado.
    Cada endpoint es independiente y puede consumirse por separado.
    """,
    version     = "1.0.0"
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar cada endpoint ───────────────────────────────────────────────────
app.include_router(router_diagnostico)  # POST /doctor/diagnostico
app.include_router(router_orden)        # POST /doctor/orden-medica
app.include_router(router_receta)       # POST /doctor/receta
app.include_router(router_pacientes)    # GET  /doctor/{id}/pacientes-atendidos
app.include_router(router_consulta)     # GET  /doctor/consulta-paciente
app.include_router(router_recetas)      # GET  /doctor/recetas-paciente

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["ServicioDoctores"])
def raiz():
    """Verifica que el servicio está activo"""
    return {
        "servicio" : "ServicioDoctores - EcoSistemaSalud",
        "estado"   : "activo",
        "version"  : "1.0.0",
        "endpoints": [
            "POST /doctor/diagnostico",
            "POST /doctor/orden-medica",
            "POST /doctor/receta",
            "GET  /doctor/{id}/pacientes-atendidos",
            "GET  /doctor/consulta-paciente",
            "GET  /doctor/recetas-paciente"
        ]
    }

# ── Panel visual del doctor ───────────────────────────────────────────────────
@app.get("/panel", tags=["Panel"], include_in_schema=False)
def panel_doctor():
    """Sirve el panel visual HTML del doctor"""
    panel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "panel_doctor.html")
    return FileResponse(panel_path)

# ── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        print("=" * 55)
        print("[*] ServicioDoctores - EcoSistemaSalud")
        print("[*] Puerto : 8001")
        print("[*] Docs   : http://localhost:8001/docs")
        print("[*] Panel  : http://localhost:8001/panel")
        print("=" * 55)
        uvicorn.run(
            "main:app",
            host      = "0.0.0.0",
            port      = 8001,
            reload    = True,
            log_level = "info"
        )
    except KeyboardInterrupt:
        print("\n[!] Interrupción detectada por el usuario.")
    except Exception as e:
        print(f"\n[!] Error inesperado: {e}")
    finally:
        print("[*] Proceso finalizado. Puerto liberado.")
        sys.exit(0)