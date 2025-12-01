# 🎯 Quest 1: Demo Comercial V1 (SmartOps Core)

**Objetivo:** Cerrar ventas en caliente mostrando un bot personalizado en segundos.
**Filosofía:** "En una llamada te muestro tu propio bot". Sin instalaciones, sin esperas.

## 🔄 Flujo de la Demo (The Magic Loop)

1.  **El Gancho:** "Pásame tu menú/catálogo por WhatsApp".
2.  **The Loader (Ingesta):**
    * `POST /demo/upload` -> FastAPI procesa PDF/Img -> Genera Contexto Vectorial.
    * Se crea una `session_id` temporal.
3.  **El Show (Interacción):**
    * Cliente escribe al Bot Demo (Waha).
    * `POST /demo/message` -> RAG busca en el contexto temporal -> Responde como el negocio del cliente.
4.  **The Neuralizer (Cierre):**
    * `POST /demo/reset` -> Borra contexto temporal.
    * Bot olvida todo y queda listo para el siguiente cliente.
    * Se guarda el Lead en BD.

## 📊 Estado del Dato (Modelo Mental)

### Entidad: DemoSession
* `session_id` (UUID): Identificador único de la demo actual.
* `status`: "active" | "closed".
* `context_expiry`: Timestamp (Auto-limpieza si se nos olvida el Neuralizer).

### Entidad: DemoLead (Lo que vale dinero)
* `nombre_prospecto`: String.
* `whatsapp_contacto`: String.
* `tipo_negocio`: "Restaurante" | "Clínica" | "Agencia".
* `nivel_interes`: "Caliente" (Quiere comprar) | "Tibio" | "Frío".
* `archivo_original`: Path al archivo subido.
