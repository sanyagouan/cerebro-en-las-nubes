# 🦅 MANUAL OPERATIVO DE SALA: SISTEMA DE GESTIÓN DE RESERVAS

Este documento define la **configuración única y óptima** para que tu equipo gestione las reservas de "En las Nubes" con velocidad y cero errores.
No hay opciones. Esta es la mejor forma de hacerlo usando Airtable Interfaces.

---

## 🎯 OBJETIVO

Crear un **"Panel de Mando (Maître)"** que se use en una Tablet o Móvil durante el servicio.

- **Solo muestra las reservas de HOY** (Automático).
- **Gestión visual**: Arrastrar y soltar para sentar mesas.
- **Seguridad**: El personal NO puede romper la base de datos ni ver datos antiguos innecesarios.

---

## ⚙️ PARTE 1: CONFIGURACIÓN TÉCNICA (Hazlo tú una vez)

Sigue estos pasos exactos desde tu ordenador (Vista Admin):

### 1. Crear la Interfaz "Servicio de Sala"

1. En Airtable, arriba a la izquierda, pulsa **"Interfaces"** > **"Start building"**.
2. Dale nombre: **"🛎️ RECEPCIÓN / SALA"**.
3. Elige el tipo: **"Kanban"** (Es la opción más visual para flujo de trabajo).
4. Conecta a la tabla: **"Reservas"**.

### 2. Configurar el Filtro de Hierro (CRÍTICO)

Para que el camarero no se confunda con reservas de la semana que viene:

1. En la configuración del Kanban, busca la sección **"Filter"** (Filtro).
2. Añade esta condición EXACTA:
   - `Fecha de Reserva` **is** `Today` (Es hoy).
   - *(Opcional)*: Añade un grupo con `OR` -> `Fecha de Reserva` **is** `Tomorrow` (si quieres que vean previsión, pero recomiendo SOLO HOY para máxima concentración).

### 3. Configurar las Columnas (Estados)

El Kanban debe tener estas columnas basadas en tu campo `Estado de Reserva`:

1. **Pendiente**: Reservas que entran por la IA/Web y nadie ha mirado.
2. **Confirmada**: El cliente ha reconfirmado (o hemos llamado).
3. **Sentada (En Mesa)**: El cliente ha llegado y está comiendo.
4. **Completada**: Ya se han ido (o No Show).

### 4. Configurar la Tarjeta (Lo que ven)

Edita la "Card" para que muestre SOLO lo vital, en este orden:

1. **Hora** (Ponlo en negrita o grande).
2. **Nombre del Cliente**
3. **Cantidad de Personas** (Pax)
4. **Teléfono** (Botón directo para llamar si hay retraso).
5. **Notas** (Alergias, trona, etc).
6. **Mesa** (Campo editable para asignar mesa al llegar).

---

## 📱 PARTE 2: FLUJO DE TRABAJO DEL PERSONAL (Imprime esto para ellos)

### PROTOCOLO DE SERVICIO

**1. Al iniciar el turno:**

- Abre la App de Airtable en la Tablet/Móvil.
- Entra en **"🛎️ RECEPCIÓN / SALA"**.
- Verás **solo las reservas de hoy** ordenadas por hora.

**2. Cuando entra una reserva nueva (IA):**

- Aparece automáticamente en la columna **"Pendiente"**.
- Si llamáis para confirmar, arrástrala a **"Confirmada"**.

**3. Cuando llega el cliente (Check-in):**

- Busca el nombre en la tarjeta.
- **Asigna la Mesa**: Toca el campo "Mesa" y selecciona la mesa libre.
- **Arrastra la tarjeta** a la columna **"Sentada"**.
- *Efecto:* Esto bloquea la mesa en el sistema para que la IA no la reserve de nuevo.

**4. Cuando se van (Check-out):**

- Arrastra la tarjeta a **"Completada"**.
- Esto libera la mesa para el siguiente turno.

---

## �️ POR QUÉ ESTO ES LO MEJOR

- **Velocidad**: Arrastrar es más rápido que entrar, editar y guardar.
- **Foco**: Al filtrar por "Hoy", eliminas el 90% del ruido visual.
- **Cero Errores**: Al no dar acceso a la "Grid View" (Excel), nadie puede borrar una columna por error ni desconfigurar la base de datos.
- **Tiempo Real**: Si la IA mete una reserva a las 21:00, aparece al instante en la pantalla del Maître.

---

## 🔐 PARTE 3: SEGURIDAD Y PERMISOS (Solo para ti)

Para mantener el control total como Dueño/a, configura los accesos así:

### 1. Camareros (Acceso "Solo Ver y Mover")

Queremos que vean el tablero y muevan tarjetas, pero que NO toquen configuraciones.

- **Cómo invitar**: Comparte solo la **Interfaz**, no la base de datos entera.
- **Rol en la Interfaz**: `Commenter` (si solo quieres que miren) o `Editor` (si quieres que arrastren tarjetas).
- **Truco Pro**: No les des login. En la tablet del restaurante, deja la sesión iniciada con una cuenta genérica (`sala@tuweb.com`) que solo tenga acceso a esa Interfaz.

### 2. Encargada (Acceso "Supervisor")

Necesita ver calendarios mensuales y listas de clientes VIP.

- **Acceso**: Dale acceso a la **Base de Datos** completa.
- **Rol**: `Editor`.
- **Qué puede hacer**: Modificar reservas pasadas, ver estadísticas, exportar excel.
- **Qué NO puede hacer**: Borrar tablas o cambiar fórmulas (para eso se necesita rol `Creator`, que eres tú).

### 3. Dueño/Admin (Tú)

- **Rol**: `Creator` u `Owner`.
- Control total de facturación, automatizaciones IA y diseño de base de datos.
