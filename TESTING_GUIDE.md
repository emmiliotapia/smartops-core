# Guía de Pruebas - SmartOps Core v4.0 Quest 1

## Descripción General

Este directorio contiene scripts de prueba para validar los 3 endpoints del módulo **Demo Router** (Quest 1: Demo Comercial):

1. **THE LOADER** (`POST /demo/upload`) - Ingesta de documentos
2. **THE SHOW** (`POST /demo/message`) - Interacción con bot
3. **THE NEURALIZER** (`POST /demo/reset`) - Cierre de sesión
4. **HEALTH CHECK** (`GET /demo/health`) - Estado del módulo

## Archivos de Prueba

### 1. `menu_dummy.pdf`
Archivo PDF simulado con contenido de menú. Se usa como documento de entrada para la prueba del LOADER.

```bash
# Crear manualmente si no existe:
echo "Menu de Prueba: Pizza $10, Tacos $5" > menu_dummy.pdf
```

### 2. `test_demo_endpoints.ps1` (PowerShell)
Script para Windows PowerShell que prueba los 3 endpoints de forma secuencial.

**Uso:**
```powershell
# Ejecutar con configuración por defecto
.\test_demo_endpoints.ps1

# Ejecutar con URL y secreto personalizados
.\test_demo_endpoints.ps1 -ApiUrl "http://localhost:8000" -SecretWord "mypassword"

# Ver ayuda
Get-Help .\test_demo_endpoints.ps1 -Full
```

**Parámetros:**
- `-ApiUrl`: URL de la API (default: `http://localhost:8001`)
- `-FilePath`: Ruta del archivo PDF (default: `menu_dummy.pdf`)
- `-SecretWord`: Palabra secreta NEURALIZER (default: `flash`)

### 3. `test_demo_api.py` (Python)
Script Python más robusto con validaciones, manejo de errores mejorado y colores en la terminal.

**Uso:**
```bash
# Ejecutar con configuración por defecto
python test_demo_api.py

# Ejecutar con parámetros personalizados
python test_demo_api.py --api-url http://localhost:8000 --secret mypassword --file /ruta/a/archivo.pdf

# Ver ayuda
python test_demo_api.py --help
```

**Parámetros:**
- `--api-url`: URL de la API (default: `http://localhost:8001`)
- `--secret`: Palabra secreta NEURALIZER (default: `flash`)
- `--file`: Ruta del archivo PDF (default: `menu_dummy.pdf`)

**Requisitos Python:**
```bash
pip install requests
```

## Flujo de Prueba Completo

```
┌─────────────────────────────────────────────────────────────┐
│ 1. THE LOADER (POST /demo/upload)                          │
│    - Carga archivo PDF con metadatos                       │
│    - Crea DemoSession en BD                                │
│    - Retorna session_id                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. THE SHOW (POST /demo/message)                           │
│    - Envía mensaje a la sesión activa                      │
│    - Bot responde contextualizado por business_type        │
│    - Valida que sesión esté activa                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. THE NEURALIZER (POST /demo/reset)                       │
│    - Valida palabra secreta                                │
│    - Cierra sesión (active=False)                          │
│    - Opcionalmente crea DemoLead                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. HEALTH CHECK (GET /demo/health)                         │
│    - Verifica estado del módulo                            │
│    - Retorna información de versión                        │
└─────────────────────────────────────────────────────────────┘
```

## Preparación para Pruebas

### Paso 1: Instalar Dependencias

```bash
cd c:\smartopsia\smartops-core
pip install -r app/requirements.txt
```

### Paso 2: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Database
DATABASE_URL=postgresql://root:<password>@localhost:5433/smartops_core

# Security
NEURALIZER_SECRET=flash

# API
API_HOST=0.0.0.0
API_PORT=8001
```

### Paso 3: Iniciar la API

```bash
# Opción 1: Con uvicorn directamente
cd c:\smartopsia\smartops-core
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Opción 2: Con Docker (si tienes docker-compose.yml)
docker-compose up -d
```

### Paso 4: Ejecutar Pruebas

**Con PowerShell (Windows):**
```powershell
cd c:\smartopsia\smartops-core
.\test_demo_endpoints.ps1
```

**Con Python:**
```bash
cd c:\smartopsia\smartops-core
python test_demo_api.py
```

## Ejemplos de Respuestas Esperadas

### THE LOADER - Respuesta Exitosa
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "message": "Sesion de demo iniciada para Pizzeria Jarvis (restaurante)"
}
```

### THE SHOW - Respuesta Exitosa
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Bienvenido a Pizzeria Jarvis! Soy tu asistente de IA. Te preguntaste: 'Hola, ¿tienen pizza?' Tenemos un excelente menu ejecutivo para hoy.",
  "business_type": "restaurante"
}
```

### THE NEURALIZER - Respuesta Exitosa
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "closed",
  "message": "Sesion de demo cerrada exitosamente para Pizzeria Jarvis",
  "lead_saved": true
}
```

### HEALTH CHECK - Respuesta Exitosa
```json
{
  "status": "healthy",
  "module": "demo",
  "version": "1.0.0"
}
```

## Resolución de Problemas

### Error: "No se puede conectar a http://localhost:8001"
- **Causa**: La API no está corriendo
- **Solución**: Inicia la API con `uvicorn app.main:app --port 8001`

### Error: "Archivo no encontrado: menu_dummy.pdf"
- **Causa**: El archivo PDF no existe en el directorio actual
- **Solución**: Crea el archivo dummy o especifica la ruta correcta

### Error: "Palabra secreta incorrecta"
- **Causa**: La palabra secreta no coincide
- **Solución**: Verifica que `NEURALIZER_SECRET` en `.env` sea "flash" (o usa `--secret flash`)

### Error: "Sesion no encontrada" (en THE SHOW o THE NEURALIZER)
- **Causa**: El session_id no es válido o la sesión expiró
- **Solución**: Ejecuta nuevamente desde el LOADER para obtener un nuevo session_id

### Error: 500 en base de datos
- **Causa**: La base de datos no está conectada
- **Solución**: Verifica que PostgreSQL esté corriendo y que DATABASE_URL sea correcta

## Casos de Prueba Adicionales

### Prueba de Sesión Cerrada
```python
# Después de ejecutar NEURALIZER, intentar enviar mensaje a sesión cerrada
payload = {
    "session_id": "mismo_session_id",
    "message": "test"
}
# Esperado: Error 400 "La sesion de demo ha sido cerrada"
```

### Prueba de Palabra Secreta Incorrecta
```python
payload = {
    "session_id": "session_id_valido",
    "secret_word": "wrong_password",
    "save_lead": True
}
# Esperado: Error 403 "Palabra secreta incorrecta"
```

### Prueba de Session_id Inválido
```python
payload = {
    "session_id": "invalid-uuid",
    "message": "test"
}
# Esperado: Error 404 "Sesion ... no encontrada"
```

## Monitoreo y Logging

La API genera logs útiles durante la ejecución. Para aumentar el nivel de detalle:

**En `app/main.py`:**
```python
# Cambiar a True para ver queries SQL
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Ver SQL queries
)
```

**En terminal:**
```bash
# Ver logs en tiempo real
tail -f logs/api.log
```

## Notas Importantes

1. **Palabra Secreta**: Por defecto es "flash", pero se puede configurar vía variable de entorno `NEURALIZER_SECRET`

2. **Almacenamiento de Archivos**: Los PDF se guardan en `/tmp/smartops_demo_uploads/` (configurable)

3. **Datos Dummy en Lead**: Actualmente el lead se crea con datos ficticios. En producción se debe extraer del contexto de la sesión.

4. **Mock Responses**: Las respuestas del bot son basadas en business_type pero sin integración RAG real (TODO)

5. **UUIDs**: Todas las sesiones y leads usan UUIDs v4 para garantizar unicidad

## Próximos Pasos

- [ ] Integrar RAG real en THE SHOW
- [ ] Capturar datos de prospecto en UI
- [ ] Guardar logs de conversación
- [ ] Implementar persistencia de vectors en pgvector
- [ ] Agregar autenticación/autorización
- [ ] Crear dashboard de analytics

## Soporte

Para reportar problemas o sugerencias, contacta a: dev@smartops.local
