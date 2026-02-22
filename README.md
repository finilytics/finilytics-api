# Finilytics API

API de análisis inteligente de documentos financieros y contables.

## Endpoints

- `POST /procesar` - Procesar archivo contable
- `GET /health` - Verificar estado del servicio
- `GET /` - Información general

## Uso

```bash
curl -X POST "https://api-finilytics.railway.app/procesar" \
  -F "archivo=@tu-archivo.xlsx"
