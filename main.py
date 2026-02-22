from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import time
from datetime import datetime

app = FastAPI(
    title="Finilytics API",
    description="API de análisis inteligente de documentos financieros",
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
async def procesar_documento(archivo: UploadFile = File(...)):
    """
    Endpoint principal - Formato compatible con Base44
    """
    try:
        # Leer archivo
        contenido = await archivo.read()
        nombre = archivo.filename.lower()
        extension = nombre.split('.')[-1]
        
        # Detectar tipo de archivo
        if extension in ['xlsx', 'xls', 'csv']:
            file_type = detectar_tipo_reporte(nombre, contenido)
        else:
            file_type = "otro"
        
        # Generar análisis según tipo
        analysis = generar_analisis(file_type, nombre)
        
        return {
            "success": True,
            "file_type": file_type,
            "analysis": analysis
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def detectar_tipo_reporte(nombre: str, contenido: bytes) -> str:
    """Detecta el tipo de reporte basado en el nombre"""
    nombre_lower = nombre.lower()
    
    if any(x in nombre_lower for x in ['coste', 'costo', 'venta', 'margen']):
        return "coste_ventas"
    elif any(x in nombre_lower for x in ['compra', 'proveedor', 'gasto']):
        return "compras"
    elif any(x in nombre_lower for x in ['pago', 'banco', 'transferencia']):
        return "pagos_banco"
    elif any(x in nombre_lower for x in ['inventario', 'stock', 'producto']):
        return "inventario"
    else:
        return "otro"

def generar_analisis(file_type: str, nombre: str) -> dict:
    """Genera el análisis en formato Base44"""
    
    # Fechas de ejemplo (en producción se extraen del archivo)
    hoy = datetime.now()
    inicio_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
    fin_mes = hoy.strftime("%Y-%m-%d")
    
    base_analysis = {
        "data_category": "mixed",
        "period_start": inicio_mes,
        "period_end": fin_mes
    }
    
    if file_type == "coste_ventas":
        return {
            **base_analysis,
            "data_category": "cost_of_goods",
            "ingresos": 50000,
            "costo_ventas": 30000,
            "gastos_operativos": 5000,
            "nomina": 3000,
            "inventario_comprado": 2000,
            "entradas_banco": 10000,
            "salidas_banco": 8000
        }
    
    elif file_type == "compras":
        return {
            **base_analysis,
            "data_category": "operating_expenses",
            "clasificaciones": {
                "Proveedor A": {
                    "rol": "COSTO_VENTAS",
                    "subcategoria": "Materia prima",
                    "monto": 15000.00
                },
                "Proveedor B": {
                    "rol": "GASTO_OPERATIVO", 
                    "subcategoria": "Servicios",
                    "monto": 2500.50
                }
            },
            "gastos_operativos": 2500.50,
            "nomina": 0,
            "inventario_comprado": 15000.00,
            "entradas_banco": 0,
            "salidas_banco": 17500.50
        }
    
    elif file_type == "inventario":
        return {
            **base_analysis,
            "data_category": "inventory",
            "productos": [
                {
                    "nombre": "Producto A",
                    "cantidad": 100,
                    "valor_unitario": 50.00,
                    "valor_total": 5000.00
                },
                {
                    "nombre": "Producto B",
                    "cantidad": 50,
                    "valor_unitario": 75.00,
                    "valor_total": 3750.00
                }
            ],
            "gastos_operativos": 0,
            "nomina": 0,
            "inventario_comprado": 8750.00,
            "entradas_banco": 0,
            "salidas_banco": 0
        }
    
    else:
        return {
            **base_analysis,
            "data_category": "mixed",
            "gastos_operativos": 0,
            "nomina": 0,
            "inventario_comprado": 0,
            "entradas_banco": 0,
            "salidas_banco": 0
        }

@app.get("/health")
def health_check():
    return {
        "status": "operational",
        "servicio": "finilytics-api",
        "version": "1.0.0-base44-compatible"
    }

@app.get("/")
def root():
    return {
        "bienvenido_a": "Finilytics API",
        "version": "Base44 Compatible",
        "endpoints": {
            "procesar": "POST /procesar",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
