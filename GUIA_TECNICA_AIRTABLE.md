# MANUAL DE ARQUITECTURA TÉCNICA: "EN LAS NUBES" (AIRTABLE)

**Rol:** Arquitecto de Sistemas / Implementador
**Objetivo:** Construir interfaz Kanban de Sala (Tablet) a prueba de errores.

---

## 🏗️ 1. BASE DE DATOS Y CAMPOS (Backend)

No tocaremos código externo. Todo vive en Airtable.

### A. Tabla: `Reservas`

Asegura que existen estos campos. Si no, créalos con estas configuraciones exactas.

| Campo | Tipo | Configuración / Fórmula |
| :--- | :--- | :--- |
| `Fecha de Reserva` | Date | Include time: OFF |
| `Hora` | Date | Include time: ON (Formato 24h) |
| `Estado de Reserva` | Single Select | `Pendiente`, `Confirmada`, `Sentada`, `Completada`, `No Show`, `Cancelada` |
| `Mesa` | Linked Record | Link a tabla `Mesas` (Ver Fase PRO) o Single Select (Fase MVP) |
| `Nombre Cliente` | Single Line Text | - |
| `Pax` | Number | Integer |
| `Teléfono` | Phone | - |
| `Notas` | Long Text | - |

### B. CAMPOS DE LÓGICA (La "Magia" Oculta)

Crea estos campos **Fórmula** para gestionar la visibilidad sin que el personal toque filtros.

#### 1. Campo: `Servicio Activo`

*Este campo vale 1 solo si la reserva es para HOY y no está cancelada/completada.*

**Fórmula (Copiar y Pegar):**

```airtable
IF(
  AND(
    DATETIME_FORMAT({Fecha de Reserva}, 'YYYY-MM-DD') = DATETIME_FORMAT(NOW(), 'YYYY-MM-DD'),
    OR(
      {Estado de Reserva} = "Pendiente",
      {Estado de Reserva} = "Confirmada",
      {Estado de Reserva} = "Sentada"
    )
  ),
  1,
  0
)
```

*(Nota: Airtable usa UTC internamente. Si ves problemas de zona horaria por la noche, usa `SET_TIMEZONE({Fecha de Reserva}, 'Europe/Madrid')` para ajustar).*

#### 2. Campo: `Hora Formateada`

*Para mostrar grande en la tarjeta.*
**Fórmula:**

```airtable
DATETIME_FORMAT(SET_TIMEZONE({Hora}, 'Europe/Madrid'), 'HH:mm')
```

---

## 🎨 2. CONFIGURACIÓN DE LA INTERFACE (Frontend Maître)

1. Ve a la pestaña **Interfaces** arriba en Airtable.
2. Crea una nueva Interface llamada **"🛎️ RECEPCIÓN / SALA"**.
3. Elige Layout: **Kanban**.
4. **Configuración del Elemento Kanban**:
    * **Source Table**: `Reservas`.
    * **Filter Data**: Add Condition -> `Servicio Activo` = `1`.
        * *Esto es crucial. El filtro es automático. El camarero no puede quitarlo.*
    * **Group By (Columns)**: `Estado de Reserva`.
    * **Visible Groups**: Activa solo `Pendiente`, `Confirmada`, `Sentada`. (Oculta el resto para limpieza, o deja `Completada` al final).
    * **Sort By**: `Hora` (Ascendente 0-9).

5. **Diseño de la Tarjeta (Card)**:
    * **Header**: `Hora Formateada` (Hazlo Bold).
    * **Secondary Field**: `Nombre Cliente`.
    * **Body Fields**: `Pax` (👥), `Mesa` (🪑), `Notas` (📝).

6. **Permisos de Edición (Seguridad)**:
    * Haz click en la tarjeta en el modo edición.
    * En el panel derecho "Editable Fields": **Selected fields only**.
    * Marca SOLO: `Mesa` y `Estado de Reserva`.
    * El resto (Nombre, Hora, etc.) se ven pero NO se tocan.

---

## 🚀 3. FASE PRO: BLOQUEO DE MESAS (Automations)

### A. Nueva Tabla `Mesas`

Crea una tabla separada llamada `Mesas`.

* Records: Mesa 1, Mesa 2, Mesa 3...
* Campo `Estado Actual` (Single Select): `Libre`, `Ocupada`.
* Campo `Ocupada Hasta` (Date/Time).

**En Tabla `Reservas`:**

* Convierte el campo `Mesa` a **Link to another record** -> `Mesas`.

### B. Automation 1: "Bloquear Mesa"

**Trigger**: Airtable Automation > "When record matches conditions".

* Table: `Reservas`.
* Condition: `Estado de Reserva` = `Sentada` AND `Mesa` is not empty.

**Action**: "Update record".

* Table: `Mesas`.
* Record ID: Selecciona (Step 1 > Mesa > Record ID).
* Fields:
  * `Estado Actual` -> `Ocupada`.
  * `Ocupada Hasta` -> *Aquí hay truco en Airtable puro. Sin scripts, no puedes sumar horas fácil en una Automation Action standard.*

**Solución PRO (Con Script Sencillo):**
Cambia la **Action** a "Run Script".

**Script (Copiar y Pegar):**

```javascript
// Script para Bloquear Mesa + 2 Horas
let inputConfig = input.config();
let mesaId = inputConfig.mesaId; // Tienes que definir esta variable en el panel izquierdo del script

if (mesaId && mesaId.length > 0) {
    let table = base.getTable("Mesas");
    let ahora = new Date();
    let hasta = new Date(ahora.getTime() + (2 * 60 * 60 * 1000)); // +2 Horas

    await table.updateRecordAsync(mesaId[0], {
        "Estado Actual": "Ocupada",
        "Ocupada Hasta": hasta
    });
}
```

*(Para usar este script, en el panel izquierdo de la automatización, añade Input Variable: `mesaId` = Step 1 > Mesa > Record ID).*

### C. Automation 2: "Liberar Mesa"

**Trigger**: `Reservas` > `Estado de Reserva` cambia a `Completada`.
**Action**: "Update record" (Table `Mesas`).

* Fields: `Estado Actual` -> `Libre`, `Ocupada Hasta` -> (vacío).

---

## 🔒 4. SEGURIDAD

**Usuario Sala (Tablet):**

1. Si tu plan es **Free/Plus**: El usuario DEBE ser **Editor** de la base para mover tarjetas.
    * **Protección**: No le des acceso a la vista "Grid" completa. Crea una vista "Bloqueada" en la tabla.
    * **Acceso**: Envíale a la tablet SOLO la URL de la Interface (`airtable.com/app.../pag...`).
2. Si tu plan es **Business/Enterprise**:
    * Hazlo "Read Only" en la base.
    * Dale permiso explícito de Edición solo en la Interface.

**En la Tablet:**

1. Abre el link de la Interface en Chrome/Safari.
2. Menú opciones -> "Añadir a Pantalla de Inicio".
3. Esto crea un icono de App que abre la interface a pantalla completa (Modo Kiosco).

---

Tu sistema está listo. Empieza por la **FASE 1 y 2 (MVP)** hoy mismo.
