# Configuración Real de Mesas - Restaurante Verdent

> **Fuente**: Capturas del software Agora (sistema actual en uso)
> **Fecha**: 12 febrero 2026
> **Estado**: Recién instalado, requiere optimización

---

## 🏪 BARRA (2 mesas reservables + banquetas no reservables)

### Mesas Reservables
- **B1**: Mesa alta con banquetas, 2 personas (3 máx, incómodo)
- **B2**: Mesa alta con banquetas, 2 personas (3 máx, incómodo)

**Características:**
- Uso secundario: solo cuando terraza/comedor llenos
- Requiere avisar al cliente de la incomodidad si 3 personas
- Banquetas individuales NO reservables (solo consumiciones rápidas)

**Reglas de Asignación:**
- Prioridad baja (última opción)
- Solo para grupos de 2 (máx 3 con advertencia)
- Verificar disponibilidad en terraza/sala primero

---

## 🌳 TERRAZA (16 mesas visibles, configuración dinámica)

### Layout Actual en Agora

**Fila Superior:**
- T9, T10, T11, T12, T13, T14, T15, T16 (8 mesas)

**Fila Inferior:**
- T1, T2, T3, T4, T5, T6, T7, T8 (8 mesas)

### Capacidades Base
- **Mesa individual**: 4 personas
- **2 mesas juntas**: 6 personas máximo
- **Total mesas**: 16 unidades físicas

### ⚠️ PROBLEMA: Configuración Dinámica

**Factores que condicionan la distribución:**
1. Elementos urbanos (árboles, bancos, señales)
2. Clima (lluvia, viento, sol directo)
3. Ocupación previa (mesas ya juntadas)
4. Espacio peatonal requerido

**Estado actual:**
- Número de mesas visible: 16
- Configuraciones posibles: PENDIENTE DE DOCUMENTAR
- Combinaciones válidas: PENDIENTE DE VALIDAR CON OPERACIONES
- Restricciones físicas: PENDIENTE DE MAPEAR

**Acción requerida:**
- [ ] Documentar qué mesas se pueden juntar (ej: T1+T2, T3+T4)
- [ ] Identificar mesas que NO se pueden mover por obstáculos fijos
- [ ] Definir capacidad máxima real de terraza en servicio típico
- [ ] Establecer configuraciones por defecto según demanda

---

## 🍽️ SALA / COMEDOR (17 posiciones identificadas)

### Mesas Principales

**S1** - Mesa rectangular, 4 personas
**S2** - Mesa rectangular GRANDE, 6-8 personas (¿ampliable?)
**S3** - Mesa rectangular, 4 personas
**S4** - Mesa rectangular, 4 personas
**S5** - Mesa rectangular, 4 personas
**S6** - Mesa rectangular, 6 personas
**S7** - Mesa rectangular, 6 personas
**S8** - Mesa rectangular, 4 personas

### Zona Sofás (4 posiciones)

**SOFA 1** - 2-4 personas
**SOFA 2** - 2-4 personas (¿ampliable según captura?)
**SOFA 3** - 2-4 personas
**SOFA 4** - 2-4 personas

### Mesas B en Sala

**B5** - Mesa en sala, 4 personas
**B8** - Mesa en sala, 4 personas

### 📝 Notas Importantes

**Estado actual:**
- Configuración recién instalada en Agora
- Requiere optimización según reglas del negocio
- Falta definir mesas ampliables y auxiliares
- Falta documentar ubicaciones especiales (ventana, baño, etc.)

**Preguntas pendientes:**
- [ ] ¿Qué mesas son ampliables y con qué auxiliares?
- [ ] ¿S2 es ampliable? (parece grande en la captura)
- [ ] ¿SOFA 2 es ampliable? (aparece más grande)
- [ ] ¿Hay mesas auxiliares físicas disponibles?
- [ ] ¿Ubicaciones especiales a documentar? (ventana, junto al baño, etc.)
- [ ] ¿Capacidades exactas de cada mesa en la práctica?

---

## 📊 RESUMEN CUANTITATIVO

| Zona | Mesas Identificadas | Capacidad Aprox | Estado Documentación |
|------|--------------------:|----------------:|---------------------|
| Barra | 2 + banquetas | 4-6 personas | ✅ Completo |
| Terraza | 16 | 64+ (variable) | ⚠️ Dinámico - Requiere mapeo |
| Sala | 17 posiciones | ~70-80 personas | ⚠️ Pendiente capacidades exactas |
| **TOTAL** | **35** | **~140-150** | 🔄 En proceso |

---

## 🎯 PRÓXIMOS PASOS

### Inmediatos
1. Validar capacidades exactas de cada mesa de sala
2. Identificar mesas ampliables y sus auxiliares
3. Mapear configuraciones válidas de terraza

### Corto Plazo
4. Documentar restricciones físicas de terraza (árboles, bancos)
5. Establecer reglas de prioridad de asignación
6. Definir configuraciones por defecto según demanda

### Medio Plazo
7. Diseñar schema de Airtable que capture esta complejidad
8. Implementar sistema de configuraciones dinámicas
9. Integrar con algoritmo de asignación inteligente

---

**Última actualización**: 12 febrero 2026
**Responsable**: Sistema Verdent Assistant
**Próxima revisión**: Pendiente validación con operaciones
