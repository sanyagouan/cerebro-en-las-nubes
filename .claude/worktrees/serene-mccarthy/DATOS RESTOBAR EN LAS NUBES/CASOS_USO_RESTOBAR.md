# CASOS DE USO Y REGLAS DE NEGOCIO - EN LAS NUBES RESTOBAR

**Extraído de ARQUITECTURA_COMPLETA_RESTOBAR.md (2025-12-25)**

---

## 🪑 DISTRIBUCIÓN DE MESAS

### Zona Interior (13 mesas)
- **Mesas Estándar (8):**
  - T1, T2, T3, T4: 4 personas cada una
  - T5, T6: 6 personas cada una
  - T7, T8: 2 personas cada una

- **Mesas Especiales (5):**
  - C1, C2: 2 personas (accesibilidad)
  - C3: 6 personas (junto a ventana)
  - C4, C5: 4 personas (esquineras)

### Zona Terraza (8 mesas)
- **Mesas Estándar (6):**
  - TERRAZA-1, TERRAZA-2: 6 personas
  - TERRAZA-3, TERRAZA-4: 4 personas
  - TERRAZA-5: 8 personas (grande)
  - TERRAZA-6: 2 personas (íntima)

- **Mesas Especiales (2):**
  - TERRAZA-C1: 10 personas (grupo grande)
  - TERRAZA-C2: 12 personas (máxima capacidad)

### Capacidad Total: **123 personas**
- **Interior:** 59 personas (8×4 + 2×6 + 2×2 + 1×6 + 2×4)
- **Terraza:** 64 personas (2×6 + 2×4 + 1×8 + 1×2 + 1×10 + 1×12)

---

## 📅 REGLAS DE NEGOCIO

### Días Cerrados
- **Lunes:** CERRADO (excepto festivos)
- **Domingo noche:** CERRADO
- **Martes noche:** Si el lunes fue festivo, el martes también se cierra
- **Regla especial:** Si el lunes es festivo, el cierre pasa al martes por la noche del último día festivo y al día siguiente

### Turnos Dinámicos
- **Viernes/Sábado:** 2 turnos disponibles
- **Resto de días:** 1 turno
- **Grupos ≥7 personas:** Solo Turno 1 disponible en alta demanda

### Restricciones Especiales

#### Cachopo Sin Gluten
- **Requiere:** Aviso mínimo de 24 horas
- **Motivo:** Requiere protocolo especial sin contaminación
- **Importancia:** Alta por seguridad alimentaria

#### Tronas
- **Cantidad:** Máximo 2 tronas disponibles
- **Recomendación:** Reservar con antelación
- **Importancia:** Media por disponibilidad limitada

#### Mascotas
- **Permitidas:** SOLO en terraza
- **Prohibidas:** En interior del restaurante

#### Parking
- **No propio:** El restaurante no tiene aparcamiento
- **Cercanos:**
  - Calle Pérez Galdós
  - Calle República Argentina
  - Calle Huesca
  - **Parking de Gran Vía** (muy cercano)
- **Nota:** La calle del restaurante es peatonal (no se puede aparcar en la puerta)

### Horarios

#### Comidas
- **Días:** Martes a Domingo
- **Horario:** 13:30 - 17:30
- **Menú del día:**
  - Disponible: Martes a viernes mediodía
  - Horario: Hasta las 16:00 (cierra cocina a las 16:00)
  - **No disponible:** Fines de semana ni festivos

#### Cenas
- **Jueves:** 20:00 - 24:00
- **Viernes:** 20:00 - 00:30
- **Sábados:**
  - **Comida:** 13:00 - 17:30
  - **Cena:** 20:00 - 01:00
- **Domingos:** Solo comida 13:00 - 17:30

#### Resumen Horarios
- **Abierto:** Martes a Domingo
- **Cerrado:** Lunes (excepto festivos) y Domingo noche
- **Excepción:** Si el lunes es festivo → cierre en martes noche

---

## 🎯 ALGORITMO DE ASIGNACIÓN DE MESAS

### Reglas de Priorización

#### 1. Para grupos pequeños (≤2 personas)
1. Priorizar mesas íntimas o de 2 personas
2. Orden de preferencia: `baja` → `estándar` → `especial`

#### 2. Para grupos medianos (3-4 personas)
1. Priorizar mesas estándar o especiales
2. Orden de preferencia: `estándar` → `especial` → `alta`

#### 3. Para grupos medianos-grandes (5-6 personas)
1. Priorizar mesas más grandes
2. Orden de preferencia: `alta` → `estándar`

#### 4. Para grupos grandes (>6 personas)
1. Solo mesas especiales
2. Orden de preferencia: `especial` → `alta`

### Características Adicionales

Al seleccionar mesa, se prioriza según:
- **Cerca de ventana** (prioridad: 10 puntos)
- **Accesibilidad ruedas** (prioridad: 5 puntos)
- **Preferencia para grupos** (prioridad: 3 puntos)

---

## 🔢 COMBINACIONES PARA GRUPOS GRANDES

### Grupo 12-15 Personas
- **Opción A (Terraza + Interior):**
  - TERRAZA-C1 (10) + TERRAZA-3 (4) = 14 personas
  - TERRAZA-C2 (12) + T1 (4) = 16 personas

### Grupo 16-20 Personas
- **Opción B (Solo Terraza):**
  - TERRAZA-C1 (10) + TERRAZA-C2 (12) = 22 personas
  - TERRAZA-C1 (10) + TERRAZA-5 (8) + T1 (4) = 22 personas

### Grupo >20 Personas
- **Opción C (Múltiples mesas):**
  - Combinar 3-4 mesas estándar
  - Asignar mesas cercanas (coordenadas)
  - Staff especial para coordinación

---

## 📋 POLÍTICAS DE RESERVA

### Confirmaciones
- **Código de confirmación:** 8 caracteres (4 letras + 4 números)
- **Tiempo para confirmar:** 2 horas
- **Método de confirmación:** WhatsApp

### Cancelaciones
- **Tiempo de aviso:** 24 horas
- **Sin aviso:** Se puede cobrar penalización

### No-show
- **Política:** 15 minutos de tolerancia
- **Sin presentación:** Se marca como no-show en el sistema

---

## 🏪️ INFORMACIÓN DEL RESTAURANTE

### Datos Básicos
- **Nombre:** En Las Nubes Restobar
- **Dirección:** Calle María Teresa Gil de Garate, 16
- **Ciudad:** 26002 Logroño, La Rioja
- **Teléfono:** 941 57 84 51
- **Web:** En desarrollo (próximamente)

### Especialidad
- **Principal:** Cachopos (varias variedades)
- **Cocina alemana:** Salchichas y codillo
- **Otros platos:** Entrantes, hamburguesas, postres caseros

### Servicios
- **WiFi:** Gratuito
- **Aire acondicionado:** Sí
- **Calefacción:** Sí
- **Accesibilidad:**
  - Rampa de acceso: Sí
  - Silla de ruedas: Sí
  - Baños adaptados: **NO**
  - Mesas accesibles: Limitadas (avisar al reservar)

### Bebidas
- **Vino propio:** Permitido (cargo de descorche: 5€/botella)
- **Carta de vinos:** Variada con diferentes opciones
- **Cerveza artesanal:** No disponible

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-24
