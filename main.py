from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from datetime import datetime

app = FastAPI(title="Finilytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/procesar")
async def procesar_documento(archivo: UploadFile = File(...)):
    try:
        contenido = await archivo.read()
        nombre = archivo.filename.lower()
        extension = nombre.split('.')[-1]
        
        # LEER ARCHIVO REAL
        if extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(contenido))
        elif extension == 'csv':
            df = pd.read_csv(io.BytesIO(contenido))
        else:
            return {"success": False, "error": "Formato no soportado"}
        
        file_type = detectar_tipo_reporte(nombre)
        analysis = analizar_dataframe_real(file_type, df)
        
        return {
            "success": True,
            "file_type": file_type,
            "analysis": analysis
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def detectar_tipo_reporte(nombre: str) -> str:
    nombre_lower = nombre.lower()
    
    if any(x in nombre_lower for x in ['coste', 'costo', 'venta', 'margen']):
        return "coste_ventas"
    elif any(x in nombre_lower for x in ['compra', 'proveedor', 'gasto']):
        return "compras_gastos"
    elif any(x in nombre_lower for x in ['pago', 'banco', 'transferencia']):
        return "pagos_banco"
    elif any(x in nombre_lower for x in ['inventario', 'stock', 'producto']):
        return "inventario"
    return "otro"

def analizar_dataframe_real(file_type: str, df: pd.DataFrame) -> dict:
    # Detectar fechas
    fecha_cols = [col for col in df.columns if 'fecha' in str(col).lower() or 'date' in str(col).lower()]
    fechas = []
    if fecha_cols:
        fechas = pd.to_datetime(df[fecha_cols[0]], errors='coerce').dropna()
    
    period_start = fechas.min().strftime("%Y-%m-%d") if len(fechas) > 0 else None
    period_end = fechas.max().strftime("%Y-%m-%d") if len(fechas) > 0 else None
    
    # Detectar columnas numéricas
    columnas_num = df.select_dtypes(include=['number']).columns.tolist()
    
    # Detectar columna de categoría (primera columna de texto)
    columnas_texto = df.select_dtypes(include=['object']).columns.tolist()
    col_categoria = columnas_texto[0] if columnas_texto else None
    
    clasificaciones = {}
    
    if col_categoria and columnas_num:
        for _, row in df.iterrows():
            categoria = str(row[col_categoria]).strip()
            if not categoria or categoria == 'nan':
                continue
            
            # Buscar el monto (última columna numérica suele ser el total)
            monto = float(row[columnas_num[-1]]) if len(columnas_num) > 0 else 0
            
            # Clasificar automáticamente
            rol = "GASTO_OPERATIVO"
            if any(x in categoria.lower() for x in ['mercancía', 'producto', 'inventario']):
                rol = "INVENTARIO"
            elif any(x in categoria.lower() for x in ['nómina', 'sueldo', 'salario']):
                rol = "NOMINA"
            elif any(x in categoria.lower() for x in ['venta', 'ingreso']):
                rol = "INGRESO"
            
            clasificaciones[categoria] = {
                "rol": rol,
                "subcategoria": categoria,
                "monto": round(monto, 2)
            }
    
    # Calcular totales
    totales = {
        "ingresos": sum(c["monto"] for c in clasificaciones.values() if c["rol"] == "INGRESO"),
        "costo_ventas": sum(c["monto"] for c in clasificaciones.values() if c["rol"] == "COSTO_VENTAS"),
        "nomina": sum(abs(c["monto"]) for c in clasificaciones.values() if c["rol"] == "NOMINA"),
        "gastos_operativos": sum(abs(c["monto"]) for c in clasificaciones.values() if c["rol"] == "GASTO_OPERATIVO"),
        "inventario_comprado": sum(abs(c["monto"]) for c in clasificaciones.values() if c["rol"] == "INVENTARIO"),
    }
    
    return {
        "period_start": period_start,
        "period_end": period_end,
        "clasificaciones": clasificaciones,
        **totales
    }

@app.get("/health")
def health_check():
    return {"status": "operational", "version": "1.0.0"}

@app.get("/")
def root():
    return {"bienvenido_a": "Finilytics API"}
