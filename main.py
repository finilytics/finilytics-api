from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

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
        
        print(f"📂 Archivo recibido: {archivo.filename}")
        print(f"📊 Tamaño: {len(contenido)} bytes")
        
        if extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(contenido))
        elif extension == 'csv':
            df = pd.read_csv(io.BytesIO(contenido))
        else:
            return {"success": False, "error": "Formato no soportado"}
        
        print(f"✅ DataFrame cargado: {len(df)} filas x {len(df.columns)} columnas")
        print(f"📋 Columnas: {list(df.columns)}")
        print(f"🔢 Primeras 3 filas:\n{df.head(3)}")
        
        file_type = detectar_tipo_reporte(nombre)
        print(f"🏷️ Tipo detectado: {file_type}")
        
        analysis = analizar_dataframe_real(file_type, df)
        print(f"📊 Análisis: {analysis}")
        
        return {
            "success": True,
            "file_type": file_type,
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
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
    print(f"🔍 Analizando {file_type}...")
    
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Detectar columnas numéricas
    columnas_num = df.select_dtypes(include=['number']).columns.tolist()
    print(f"🔢 Columnas numéricas: {columnas_num}")
    
    # Detectar columna de categoría
    columnas_texto = df.select_dtypes(include=['object']).columns.tolist()
    print(f"📝 Columnas de texto: {columnas_texto}")
    
    col_categoria = columnas_texto[0] if columnas_texto else None
    print(f"🏷️ Columna de categoría: {col_categoria}")
    
    clasificaciones = {}
    
    if col_categoria and columnas_num:
        for idx, row in df.iterrows():
            categoria = str(row[col_categoria]).strip()
            if not categoria or categoria == 'nan' or categoria == '':
                continue
            
            # Última columna numérica suele ser el total
            monto = float(row[columnas_num[-1]]) if len(columnas_num) > 0 else 0
            
            print(f"  📌 {categoria}: ${monto}")
            
            rol = "GASTO_OPERATIVO"
            if any(x in categoria.lower() for x in ['mercancía', 'mercancia', 'producto', 'inventario']):
                rol = "INVENTARIO"
            elif any(x in categoria.lower() for x in ['nómina', 'nomina', 'sueldo', 'salario']):
                rol = "NOMINA"
            elif any(x in categoria.lower() for x in ['venta', 'ingreso']):
                rol = "INGRESO"
            
            clasificaciones[categoria] = {
                "rol": rol,
                "subcategoria": categoria,
                "monto": round(monto, 2)
            }
    
    totales = {
        "ingresos": sum(c["monto"] for c in clasificaciones.values() if c["rol"] == "INGRESO"),
        "costo_ventas": sum(c["monto"] for c in clasificaciones.values() if c["rol"] == "COSTO_VENTAS"),
        "nomina": sum(abs(c["monto"]) for c in clasificaciones.values() if c["rol"] == "NOMINA"),
        "gastos_operativos": sum(abs(c["monto"]) for c in clasificaciones.values() if c["rol"] == "GASTO_OPERATIVO"),
        "inventario_comprado": sum(abs(c["monto"]) for c in clasificaciones.values() if c["rol"] == "INVENTARIO"),
    }
    
    print(f"💰 Totales: {totales}")
    
    return {
        "period_start": None,
        "period_end": None,
        "clasificaciones": clasificaciones,
        **totales
    }

@app.get("/health")
def health_check():
    return {"status": "operational"}

@app.get("/")
def root():
    return {"bienvenido_a": "Finilytics API"}
