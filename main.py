from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import os
import time

app = FastAPI(
    title="Finilytics API",
    description="API de análisis inteligente de documentos financieros y contables",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/procesar")
async def procesar_documento(
    archivo: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """
    Endpoint principal - versión simplificada inicial
    """
    try:
        contenido = await archivo.read()
        extension = archivo.filename.lower().split('.')[-1]
        
        # Respuesta básica de prueba
        return {
            "exito": True,
            "finilytics_version": "1.0.0-beta",
            "archivo": {
                "nombre": archivo.filename,
                "extension": extension,
                "tamano_kb": round(len(contenido) / 1024, 2)
            },
            "mensaje": "Archivo recibido correctamente",
            "estado": "Procesamiento básico activo - versión completa en desarrollo"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "operational",
        "servicio": "finilytics-api",
        "version": "1.0.0-beta"
    }

@app.get("/")
def root():
    return {
        "bienvenido_a": "Finilytics API",
        "web": "https://finilytics.app",
        "endpoints": {
            "procesar": "POST /procesar",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
