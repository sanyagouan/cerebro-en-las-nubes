# Draft: App Android Completa para En Las Nubes Restobar

## Objetivo del Usuario
> "NO quiero algo mínimo viable, quiero algo COMPLETO, PROFESIONAL y FUNCIONAL 100%"

## Contexto Recuperado del AGENTS.md

### Stack Tecnológico
| Componente | Tecnología |
|------------|------------|
| Runtime | Python 3.11+ |
| Framework | FastAPI 0.115+ |
| LLMs | GPT-4o, GPT-4o-mini, DeepSeek |
| Cache | Redis 5.0+ |
| Base de Datos | Airtable (Base: appcUoRqLVqxQm7K2) |
| Comunicación | VAPI (voz), Twilio (WhatsApp/SMS) |
| Deployment | Coolify (Docker) |

### Sistema Multi-Agente
```
Cliente (Voz/WhatsApp)
         │
         ▼
    Orchestrator
         │
         ▼
    RouterAgent (gpt-4o-mini) ─── Clasifica intenciones
         │
         ├─[reservation]──▶ LogicAgent (deepseek-chat) ─── Valida disponibilidad
         │                        │
         │                        ▼
         │                   Airtable (Reservas/Mesas)
         │
         └─[human]─────────▶ HumanAgent (gpt-4o) ─── Respuestas naturales
```

### Tablas Airtable Conocidas
| Tabla | ID | Propósito |
|-------|-----|-----------|
| Reservas | tblHPyRRo18IwBAUC | Reservas del restaurante |
| Mesas | tblRSjdDIa5SrudL5 | 21 mesas (13 interior + 8 terraza) |

### Campos Reservas (conocidos)
- Nombre del Cliente
- Teléfono
- Fecha de Reserva
- Hora (DateTime)
- Cantidad de Personas
- Estado de Reserva (Pendiente/Confirmada/Cancelada)
- Mesa (linked record)
- Notas

### Campos Mesas (conocidos)
- Nombre de Mesa (Mesa 1I, Mesa 2T, etc.)
- Capacidad
- Capacidad Ampliada
- Ubicación (Interior/Terraza)
- Disponible

### Flujo de Reservas
1. Cliente llama por teléfono (VAPI)
2. VAPI transcribe y envía a Orchestrator
3. RouterAgent clasifica intención
4. LogicAgent valida disponibilidad en Airtable
5. LogicAgent asigna mesa óptima
6. HumanAgent genera respuesta natural
7. Orchestrator envía WhatsApp de confirmación (Twilio)
8. Cliente confirma por WhatsApp
9. LogicAgent actualiza estado a "Confirmada"

## Investigación en Progreso

### Agentes lanzados (4 en paralelo):
1. **bg_a2520014** - Arquitectura backend completa
2. **bg_071d5fab** - Esquema Airtable completo
3. **bg_d9a3155f** - Auditoría app Android actual
4. **bg_87f0c0ac** - Integraciones externas

### Esperando resultados para:
- [ ] Entender endpoints API existentes
- [ ] Saber qué datos hay en Airtable
- [ ] Ver qué funciona/rompe en la app
- [ ] Mapear conexiones con VAPI/Twilio

## Preguntas del Usuario Resueltas

1. **¿De dónde vienen datos de reservas?**
   - ✅ VAPI (asistente de voz) → Airtable
   - ✅ WhatsApp (Twilio) → Airtable
   - ✅ Staff humano (manual) → Airtable (pendiente verificar interfaz)

2. **¿De dónde vienen datos de carta con alérgenos?**
   - ❓ Pendiente investigar - probablemente tabla separada en Airtable o datos estáticos

3. **¿Dónde se guardan pedidos para llevar?**
   - ❓ Pendiente investigar - probablemente tabla Pedidos en Airtable

4. **¿MVP o completo?**
   - ✅ COMPLETO, PROFESIONAL, FUNCIONAL 100%

## Lo que Falta por Definir

### Datos del Restaurante
- [ ] Carta completa con 14 alérgenos
- [ ] Sistema de pedidos para llevar
- [ ] Gestión de clientes/frecuentes

### App Android
- [ ] Pantallas por rol
- [ ] Funcionalidades completas por rol
- [ ] Conexión real con backend

## Próximos Pasos
1. Esperar resultados de los 4 agentes
2. Sintetizar información
3. Crear plan COMPLETO (no MVP)
