# Base de Conocimiento (FAQs) - Agente de Voz VAPI

## Introducción

Este documento define la base de conocimiento que el agente de voz VAPI debe utilizar para responder preguntas frecuentes (FAQs) de los clientes de **En Las Nubes Restobar**.

### Propósito

Proporcionar respuestas precisas y consistentes a consultas operacionales del restaurante sin necesidad de derivar a un humano, mejorando la eficiencia del servicio y reduciendo la carga de trabajo del personal.

### Alcance

Esta base de conocimiento cubre las categorías principales de preguntas que los clientes suelen hacer por teléfono:
- Horarios y disponibilidad
- Especialidades y menú
- Restricciones dietéticas
- Servicios y comodidades
- Accesibilidad
- Política de bebidas
- Grupos y eventos
- Ubicación y contacto

### Principios de Diseño

1. **Respuestas Claras y Concisas**: Cada respuesta debe ser directa y fácil de entender en una conversación telefónica.
2. **Información Accurate**: Todas las respuestas deben reflejar las políticas actuales del restaurante.
3. **Derigir cuando sea Necesario**: Para consultas complejas o que requieren gestión humana, derivar al encargado.
4. **Tono Profesional y Amable**: Las respuestas deben mantener un tono acorde con la marca del restaurante.

---

## Categorías de FAQs

### 1. Horarios y Disponibilidad

Preguntas relacionadas con los horarios de apertura, cierre y disponibilidad del restaurante.

### 2. Especialidades y Menú

Preguntas sobre los platos principales, especialidades del restaurante y opciones del menú.

### 3. Restricciones Dietéticas

Preguntas sobre opciones sin gluten, veganas, vegetarianas y para alérgicos.

### 4. Servicios y Comodidades

Preguntas sobre las instalaciones y servicios disponibles en el restaurante.

### 5. Accesibilidad

Preguntas sobre el acceso para personas con movilidad reducida.

### 6. Política de Bebidas

Preguntas sobre la política de vinos, cervezas y otras bebidas.

### 7. Grupos y Eventos

Preguntas sobre reservas para grupos grandes y organización de eventos.

### 8. Ubicación y Contacto

Preguntas sobre la dirección, teléfono y otros datos de contacto del restaurante.

---

## Tabla Completa de FAQs

### Categoría 1: Horarios y Disponibilidad

#### ¿Tenéis menú del día?

**Respuesta**: Solo martes a viernes a mediodía, hasta las 16:00 que se cierra la cocina, el restaurante cierra a las 17:00 entre semana. No fines de semana ni festivos.

**Categoría**: Horarios y Disponibilidad

**Palabras clave**: menú del día, menú diario, comida mediodía, oferta comida, precio menú

**Notas**: Esta es una pregunta muy frecuente. La respuesta debe ser clara sobre los días y horarios específicos.

---

#### ¿A qué hora abrís y cerráis?

**Respuesta**:Abrimos de martes a viernes a las 13:00 y cerramos a las 17:00.

**Respuesta**:Abrimos los jueves a las 20:00 y cerramos a las 24:00, los viernes abrimos a las 20:00 y cerramos a las 24:30, los sábados al mediodía abrimos a las 13:00 y cerramos a las 17:30 y el sábado a la noche abrimos a las 20:00 y cerramos a la 1:00, los domingos mediodía abrimos a las 13:00 y cerramos a las 17:30.

**Dias de apertura y días de cierre. Se cierra los domingos noche y los lunes excepto si el lunes es dia festivo o días festivos consecutivos al lunes en los que se pasa el dia de cierre a la noche del ultimo dia festivo y al dia siguiente.

**Categoría**: Horarios y Disponibilidad

**Palabras clave**: hora apertura, hora cierre, horario, cuándo abren, cuándo cierran, horario atención

**Notas**: Los horarios específicos deben configurarse según la política del restaurante. Considerar diferencias entre días laborables y fines de semana.

---

#### ¿Estáis abiertos hoy?

**Respuesta**: [RESPUESTA DINÁMICA] Sí, estamos abiertos hoy hasta las [HORA CIERRE HOY]. / No, hoy estamos cerrados.

**Categoría**: Horarios y Disponibilidad

**Palabras clave**: abierto hoy, cerrado hoy, hoy abierto, hoy cerrado, disponibilidad hoy

**Notas**: Esta respuesta requiere información en tiempo real sobre el día actual y los horarios. Debe verificarse contra el calendario de festivos.

---

#### ¿Tenéis disponibilidad para hoy?

**Respuesta**: [RESPUESTA DINÁMICA] Déjame comprobar la disponibilidad para hoy. ¿A qué hora te gustaría reservar y para cuántas personas?

**Categoría**: Horarios y Disponibilidad

**Palabras clave**: disponibilidad hoy, mesa hoy, reservar hoy, hueco hoy, sitio hoy

**Notas**: Esta pregunta debe derivar al flujo de reserva. El agente debe recoger los datos necesarios (hora, número de personas) y consultar disponibilidad en Airtable.

---

### Categoría 2: Especialidades y Menú

#### ¿Cuál es vuestra especialidad?

**Respuesta**: Somos especialistas en cachopos y platos de inspiración alemana (salchichas, codillo), también tenemos una gran variedad de entrantes, hamburguesas y postres caseros.

**Categoría**: Especialidades y Menú

**Palabras clave**: especialidad, plato estrella, mejor plato, recomendación, qué cocinan

**Notas**: Destacar los dos pilares del restaurante: cachopos y cocina alemana. Esta es una pregunta clave para posicionamiento de marca.

---

#### ¿Tenéis platos alemanes?

**Respuesta**: Sí, tenemos una selección de platos de inspiración alemana, incluyendo salchichas y codillo.

**Categoría**: Especialidades y Menú

**Palabras clave**: platos alemanes, comida alemana, salchichas, codillo, cocina alemana

**Notas**: Confirmar la especialidad alemana del restaurante y mencionar ejemplos concretos.

---

#### ¿Tenéis cachopos?

**Respuesta**: Sí, los cachopos son nuestra especialidad. Tenemos varias variedades disponibles.

**Categoría**: Especialidades y Menú

**Palabras clave**: cachopo, cachopos, especialidad cachopo, tipos cachopo

**Notas**: Los cachopos son el plato estrella. La respuesta debe ser afirmativa y entusiasta.

---

#### ¿Tenéis opciones vegetarianas?

**Respuesta**: Sí, tenemos opciones vegetarianas en nuestro menú. ¿Te gustaría que te explique qué opciones tenemos?

**Categoría**: Especialidades y Menú

**Palabras clave**: vegetariano, opciones vegetarianas, comida vegetariana, sin carne

**Notas**: Confirmar disponibilidad y ofrecer más detalles si el cliente está interesado. Considerar derivar a humano para detalles específicos del menú.

---

### Categoría 3: Restricciones Dietéticas

#### ¿Tenéis cachopo sin gluten?

**Respuesta**: Sí, con aviso mínimo de 24 horas. Requiere protocolo especial sin contaminación.

**Categoría**: Restricciones Dietéticas

**Palabras clave**: cachopo sin gluten, sin gluten, celíaco, gluten free, alergia gluten

**Notas**: Esta es una respuesta crítica por seguridad alimentaria. Debe mencionar claramente el requisito de aviso previo y el protocolo especial.

---

#### ¿Tenéis opciones sin gluten?

**Respuesta**: Sí, tenemos opciones sin gluten en nuestro menú. Para el cachopo sin gluten, necesitamos aviso mínimo de 24 horas por protocolo especial.

**Categoría**: Restricciones Dietéticas

**Palabras clave**: sin gluten, gluten free, celíaco, opciones sin gluten, menú sin gluten

**Notas**: Generalizar la disponibilidad de opciones sin gluten, pero destacar el requisito especial para el cachopo.

---

#### ¿Tenéis opciones veganas?

**Respuesta**: Sí, tenemos opciones veganas disponibles en nuestro menú.

**Categoría**: Restricciones Dietéticas

**Palabras clave**: vegano, opciones veganas, comida vegana, sin productos animales

**Platos veganos**: Papas arrugadas, carpaccio de calabacin con salsa de mango y frutos secos, ensaladas variadas, tempura de verduras.

**Notas**: Confirmar disponibilidad. Considerar derivar a humano para detalles específicos del menú vegano.

---

#### ¿Tenéis opciones para alérgicos?

**Respuesta**: Sí, podemos atender a personas con alergias. Por favor, indícanos qué alergia tienes para poder asesorarte adecuadamente.

**Categoría**: Restricciones Dietéticas

**Palabras clave**: alergia, alérgico, alergias alimentarias, intolerancia, seguridad alimentaria

**Notas**: Esta es una consulta sensible que requiere información específica. Derivar a humano para garantizar la seguridad del cliente.

---

### Categoría 4: Servicios y Comodidades

#### ¿Tenéis tronas?

**Respuesta**: Sí, pero solo tenemos 2 tronas disponibles. Se recomienda reservar con antelación.

**Categoría**: Servicios y Comodidades

**Palabras clave**: tronas, silla bebé, niños, bebés, familias con niños

**Notas**: Informar sobre la disponibilidad limitada y recomendar reserva anticipada para garantizar disponibilidad.

---

#### ¿Admitís mascotas?

**Respuesta**: Las mascotas solo se admiten en terraza.

**Categoría**: Servicios y Comodidades

**Palabras clave**: mascotas, perros, animales, terraza, admisión mascotas

**Notas**: Ser claro sobre la restricción: solo en terraza, no en interior.

---

#### ¿Tenéis aparcamiento?

**Respuesta**: No, no tenemos aparcamiento propio, pero hay zonas de aparcamiento cercanas, la calle donde esta el restaurante es peatonal y en la gran via existe un parking muy cercano.

**Categoría**: Servicios y Comodidades

**Palabras clave**: aparcamiento, parking, aparcar, coche, estacionamiento

**Notas**: Configurar según la situación real del restaurante. Si no hay aparcamiento propio, ofrecer alternativas cercanas.

---

#### ¿Tenéis WiFi?

**Respuesta**: Sí, tenemos WiFi gratuito para nuestros clientes.

**Categoría**: Servicios y Comodidades

**Palabras clave**: WiFi, internet, conexión, red, wifi gratis

**Notas**: Configurar según la disponibilidad real del servicio.

---

#### ¿Tenéis aire acondicionado?

**Respuesta**: Sí, tenemos aire acondicionado.

**Categoría**: Servicios y Comodidades

**Palabras clave**: aire acondicionado, aire, climatización, fresco, temperatura

**Notas**: Configurar según la disponibilidad real del servicio.

---

#### ¿Tenéis calefacción?

**Respuesta**: Sí, tenemos calefacción.

**Categoría**: Servicios y Comodidades

**Palabras clave**: calefacción, calor, climatización, temperatura, invierno

**Notas**: Configurar según la disponibilidad real del servicio.

---

### Categoría 5: Accesibilidad

#### ¿Tenéis acceso para sillas de ruedas?

**Respuesta**: Sí, tenemos acceso para silla de ruedas, pero los baños NO están adaptados.

**Categoría**: Accesibilidad

**Palabras clave**: silla de ruedas, acceso, accesibilidad, rampa, movilidad reducida

**Notas**: Ser honesto sobre las limitaciones. El acceso está disponible, pero los baños no están adaptados. Esta información es crucial para clientes con movilidad reducida.

---

#### ¿Están los baños adaptados?

**Respuesta**: No, los baños no están adaptados para sillas de ruedas.

**Categoría**: Accesibilidad

**Palabras clave**: baños adaptados, baño accesible, WC adaptado, accesibilidad baño

**Notas**: Ser directo y claro sobre esta limitación, avisar con educación y tacto que si reservan deben avisar que van en silla de ruedas ya que hay un limite de mesas que tienen accesibilidad para silla de ruedas.

---

#### ¿Tenéis rampa de acceso?

**Respuesta**: Sí, tenemos rampa de acceso para sillas de ruedas.

**Categoría**: Accesibilidad

**Palabras clave**: rampa, acceso rampa, entrada accesible, silla de ruedas

**Notas**: Confirmar la disponibilidad de rampa para facilitar el acceso.

---

### Categoría 6: Política de Bebidas

#### ¿Se puede traer vino propio?

**Respuesta**: Sí, se permite, pero se cobra un cargo de descorche.

**Categoría**: Política de Bebidas

**Palabras clave**: vino propio, traer vino, descorche, cargo descorche, botella propia

**Notas**: Confirmar que se permite pero informar sobre el cargo adicional. El precio del descorche debe configurarse.

---

#### ¿Cuánto cobra el descorche?

**Respuesta**: El cargo de descorche es de 5 euros por botella.

**Categoría**: Política de Bebidas

**Palabras clave**: precio descorche, coste descorche, cuánto cobra, tarifa descorche

**Notas**: Configurar el precio exacto del descorche según la política del restaurante.

---

#### ¿Tenéis carta de vinos?

**Respuesta**: Sí, tenemos una carta de vinos variada con diferentes opciones.

**Categoría**: Política de Bebidas

**Palabras clave**: carta de vinos, vinos, selección vinos, vino tinto, vino blanco

**Notas**: Confirmar disponibilidad de carta de vinos. Considerar derivar a humano para detalles específicos de la carta.

---

#### ¿Tenéis cerveza artesanal?

**Respuesta**: No, no disponemos de cerveza artesanal.

**Categoría**: Política de Bebidas

**Palabras clave**: cerveza artesanal, cerveza, birra, cerveza de barril

**Notas**: Configurar según la disponibilidad real de cerveza artesanal.

---

### Categoría 7: Grupos y Eventos

#### ¿Hacéis eventos?

**Respuesta**: Sí, organizamos eventos. Para más detalles y reservas de eventos, te voy a derivar con el encargado.

**Categoría**: Grupos y Eventos

**Palabras clave**: eventos, celebraciones, fiestas, cumpleaños, eventos especiales

**Notas**: Derivar a humano para gestión de eventos, ya que requiere coordinación y detalles específicos.

---

#### ¿Aceptáis grupos grandes?

**Respuesta**: Grupos grandes (a partir de ~11 personas) requieren gestión humana. Te voy a derivar con el encargado.

**Categoría**: Grupos y Eventos

**Palabras clave**: grupos grandes, grupo, muchas personas, reserva grupo, comidas empresa

**Notas**: Definir el umbral de "grupo grande" (sugerido: 11 personas). Derivar a humano para gestión de grupos grandes.

---

#### ¿Tenéis menú para grupos?

**Respuesta**: Sí, tenemos menús especiales para grupos. Para más información y reservas, te voy a derivar con el encargado.

**Categoría**: Grupos y Eventos

**Palabras clave**: menú grupos, menú empresa, menú celebración, menú grupo grande

**Notas**: Derivar a humano para detalles de menús de grupos y reservas.

---

#### ¿Cuántas personas máximo podéis sentar?

**Respuesta**: Para más información y reservas, te voy a derivar con el encargado, el te informara mejor.

**Categoría**: Grupos y Eventos

**Palabras clave**: capacidad, máximo personas, aforo, cuántas personas, sentar

**Notas**: Configurar según la capacidad real del restaurante. Considerar diferencias entre interior y terraza si aplica.

---

### Categoría 8: Ubicación y Contacto

#### ¿Dónde estáis?

**Respuesta**: Estamos en Calle Maria Teresa Gil de Garate, 16, Logroño. ¿Necesitas más indicaciones para llegar?

**Categoría**: Ubicación y Contacto

**Palabras clave**: dónde estáis, ubicación, dirección, cómo llegar, localización

**Notas**: Proporcionar la dirección completa y ofrecer ayuda con indicaciones si es necesario.

---

#### ¿Cuál es vuestra dirección?

**Respuesta**: Nuestra dirección es Calle Maria Teresa Gil de Garate, 16, 26002, Logroño.

**Categoría**: Ubicación y Contacto

**Palabras clave**: dirección, calle, número, código postal, ciudad

**Notas**: Proporcionar la dirección completa de forma clara.

---

#### ¿Cuál es vuestro teléfono?

**Respuesta**: Nuestro teléfono es 941578451.

**Categoría**: Ubicación y Contacto

**Palabras clave**: teléfono, número, contacto, llamar, teléfono contacto

**Notas**: Proporcionar el número de teléfono principal del restaurante.

---

#### ¿Tenéis web?

**Respuesta**:  No, no disponemos de página web pero la tendremos en breve.

**Categoría**: Ubicación y Contacto

**Palabras clave**: web, página web, internet, sitio web, online

**Notas**: Configurar según la disponibilidad real de sitio web. Proporcionar la URL completa si existe.

---

## Notas de Implementación para VAPI

### Integración con el Agente de Voz

#### 1. Formato de Datos

Las FAQs deben estar en un formato que VAPI pueda consumir eficientemente. Se recomienda:

**Opción A: JSON Estructurado**
```json
{
  "faqs": [
    {
      "id": "faq_001",
      "pregunta": "¿Tenéis menú del día?",
      "respuesta": "Solo martes a viernes a mediodía, hasta las 16:00. No fines de semana ni festivos.",
      "categoria": "Horarios y Disponibilidad",
      "palabras_clave": ["menú del día", "menú diario", "comida mediodía"],
      "notas": "Pregunta muy frecuente",
      "requiere_datos_tiempo_real": false,
      "derivar_a_humano": false
    }
  ]
}
```

**Opción B: Markdown (este documento)**
- Mantener este documento como fuente de verdad
- Extraer las FAQs programáticamente para integración con VAPI
- Facilita mantenimiento por personal no técnico

#### 2. Matching de Preguntas

**Estrategia Recomendada: Similitud Semántica**

1. **Usar OpenAI Embeddings**:
   - Generar embeddings para todas las FAQs
   - Generar embedding para la pregunta del cliente
   - Calcular similitud coseno para encontrar la FAQ más relevante

2. **Umbral de Confianza**:
   - Si similitud > 0.85: Usar respuesta de FAQ automáticamente
   - Si similitud entre 0.70 y 0.85: Usar respuesta pero pedir confirmación
   - Si similitud < 0.70: Derivar a humano

3. **Palabras Clave como Filtro**:
   - Usar palabras clave para filtrar FAQs por categoría antes de calcular similitud
   - Mejora precisión y reduce tiempo de procesamiento

#### 3. Respuestas Dinámicas

Algunas FAQs requieren datos en tiempo real:

**FAQs con Datos Dinámicos**:
- ¿Estáis abiertos hoy? → Verificar día actual y horarios
- ¿Tenéis disponibilidad para hoy? → Consultar Airtable
- ¿A qué hora abrís y cerráis? → Puede variar por día de la semana

**Implementación**:
```javascript
// Ejemplo de lógica para respuesta dinámica
if (faq.requiere_datos_tiempo_real) {
  const datos = await obtenerDatosEnTiempoReal(faq.id);
  respuesta = formatearRespuesta(faq.respuesta, datos);
}
```

#### 4. Fallback y Derivación

**Cuándo Derivar a Humano**:
1. No se encuentra FAQ relevante (similitud < 0.70)
2. FAQ marcada explícitamente como `derivar_a_humano: true`
3. Consultas complejas o fuera de alcance
4. Situaciones de emergencia o quejas

**Mensaje de Derivación**:
> "Entiendo tu consulta. Para poder ayudarte mejor, voy a derivarte con nuestro encargado que te atenderá en breve."

#### 5. Arquitectura de Integración

**Flujo Recomendado**:

```
1. Cliente llama → VAPI recibe audio
2. VAPI transcribe a texto
3. n8n workflow clasifica intención:
   a) ¿Es una reserva? → Flujo de reserva
   b) ¿Es una consulta FAQ? → Flujo de FAQs
   c) ¿Otro? → Derivar a humano
4. Flujo de FAQs:
   a) Generar embedding de pregunta
   b) Buscar FAQ más similar
   c) Evaluar confianza
   d) Si confianza alta → Responder
   e) Si confianza baja → Derivar
5. VAPI convierte respuesta a voz
6. Cliente escucha respuesta
```

### Sugerencias de Implementación Técnica

#### 1. Endpoint en n8n

Crear un workflow en n8n con un webhook que VAPI pueda consultar:

**Workflow: `UTIL_FAQ_Query`**
- **Trigger**: Webhook (POST)
- **Input**: `{ "pregunta": "texto de la pregunta" }`
- **Proceso**:
  1. Generar embedding de la pregunta (OpenAI)
  2. Buscar en base de FAQs (Airtable o base de datos)
  3. Seleccionar FAQ más relevante
  4. Evaluar confianza
  5. Devolver respuesta
- **Output**: 
  ```json
  {
    "respuesta": "texto de la respuesta",
    "confianza": 0.92,
    "categoria": "Horarios y Disponibilidad",
    "derivar_a_humano": false
  }
  ```

#### 2. Almacenamiento en Airtable

**Tabla: `FAQs`**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID | Texto | Identificador único (faq_001) |
| Pregunta | Texto | Pregunta frecuente |
| Respuesta | Texto | Respuesta a la pregunta |
| Categoría | Selección | Categoría de la FAQ |
| Palabras Clave | Texto | Lista separada por comas |
| Requiere Datos Tiempo Real | Checkbox | Si necesita datos en tiempo real |
| Derivar a Humano | Checkbox | Si debe derivar a humano |
| Activa | Checkbox | Si la FAQ está activa |
| Fecha Actualización | Fecha | Última modificación |

**Ventajas de Airtable**:
- Fácil actualización por personal no técnico
- Interfaz visual para gestión
- Integración nativa con n8n
- Historial de cambios

#### 3. Caché de FAQs

**Implementación**:
- Cargar todas las FAQs en memoria al iniciar el workflow
- Actualizar caché cada X minutos o cuando se detecten cambios en Airtable
- Reducir latencia y llamadas a APIs externas

**Ejemplo**:
```javascript
// Cargar FAQs en caché
let faqsCache = null;
let lastCacheUpdate = null;

async function getFAQs() {
  const now = Date.now();
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutos
  
  if (!faqsCache || (now - lastCacheUpdate) > CACHE_TTL) {
    faqsCache = await fetchFAQsFromAirtable();
    lastCacheUpdate = now;
  }
  
  return faqsCache;
}
```

#### 4. Logging y Trazabilidad

**Registrar cada consulta FAQ**:
- Pregunta del cliente
- FAQ seleccionada
- Nivel de confianza
- Si se derivó a humano o no
- Timestamp

**Propósito**:
- Identificar FAQs faltantes o con baja confianza
- Mejorar respuestas basadas en consultas reales
- Métricas de uso del sistema

---

## Mantenimiento de la Base de Conocimiento

### Proceso de Actualización

#### 1. Identificación de Nuevas FAQs

**Fuentes**:
- Consultas frecuentes no cubiertas (revisar logs)
- Cambios en políticas del restaurante
- Feedback del personal
- Feedback de clientes

**Proceso**:
1. Revisar logs de consultas FAQs mensualmente
2. Identificar patrones de preguntas no respondidas
3. Proponer nuevas FAQs al equipo
4. Aprobar y documentar nuevas FAQs

#### 2. Actualización de FAQs Existentes

**Cuándo Actualizar**:
- Cambios en horarios
- Modificaciones en políticas (precios, restricciones)
- Nuevos servicios o eliminación de servicios
- Cambios en menú o especialidades

**Proceso**:
1. Identificar FAQ a actualizar
2. Modificar respuesta en este documento
3. Actualizar en Airtable (si se usa)
4. Invalidar caché de FAQs
5. Notificar al equipo del cambio

#### 3. Desactivación de FAQs

**Cuándo Desactivar**:
- Políticas que ya no aplican
- Servicios discontinuados
- FAQs duplicadas o redundantes

**Proceso**:
1. Marcar FAQ como inactiva en Airtable
2. Mantener registro histórico en este documento
3. Revisar logs para asegurar que no se consulta frecuentemente

#### 4. Revisión Periódica

**Frecuencia**: Trimestral

**Checklist**:
- [ ] Revisar logs de consultas FAQs
- [ ] Identificar FAQs con baja confianza
- [ ] Actualizar FAQs con información desactualizada
- [ ] Proponer nuevas FAQs basadas en tendencias
- [ ] Validar que todas las FAQs están activas y correctas
- [ ] Revisar palabras clave para mejorar matching

### Responsabilidades

| Rol | Responsabilidad |
|-----|-----------------|
| **Gerente del Restaurante** | Aprobar cambios en políticas que afectan FAQs |
| **Personal de Atención** | Reportar preguntas frecuentes no cubiertas |
| **Equipo Técnico** | Implementar actualizaciones en Airtable y n8n |
| **Equipo de Documentación** | Mantener este documento actualizado |

### Métricas de Éxito

**KPIs a Monitorear**:
1. **Tasa de Derivación a Humano**: Porcentaje de consultas que requieren derivación. Objetivo: < 20%
2. **Confianza Promedio**: Nivel de confianza promedio en las respuestas automáticas. Objetivo: > 0.85
3. **FAQs Más Consultadas**: Top 10 de FAQs más frecuentes
4. **FAQs con Baja Confianza**: FAQs que requieren mejora en respuestas
5. **Tiempo de Respuesta**: Latencia promedio en responder consultas FAQs

### Versionado

**Historial de Versiones**:

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | 2025-12-25 | Versión inicial con 8 categorías y 28 FAQs | Documentation Specialist |

---

## Anexos

### Anexo A: Campos a Configurar

Los siguientes campos en las FAQs deben configurarse con la información real del restaurante:

1. **Horarios**:
   - Hora de apertura
   - Hora de cierre
   - Diferencias entre días laborables y fines de semana

2. **Capacidad**:
   - Número máximo de personas
   - Número de tronas disponibles

3. **Servicios**:
   - Disponibilidad de aparcamiento
   - Disponibilidad de WiFi
   - Disponibilidad de aire acondicionado
   - Disponibilidad de calefacción
   - Disponibilidad de cerveza artesanal

4. **Políticas**:
   - Precio del descorche
   - Umbral de "grupo grande" (sugerido: 11 personas)

5. **Contacto**:
   - Dirección completa
   - Número de teléfono
   - URL del sitio web (si existe)

### Anexo B: Ejemplo de Integración con VAPI

**Prompt de Sistema para VAPI**:

```
Eres un asistente virtual de En Las Nubes Restobar. Tu objetivo es ayudar a los clientes con sus consultas sobre el restaurante.

INSTRUCCIONES:
1. Escucha atentamente la pregunta del cliente
2. Clasifica si es una reserva o una consulta general
3. Si es una reserva, recoge los datos necesarios (fecha, hora, número de personas, nombre, teléfono)
4. Si es una consulta general, usa la base de conocimiento de FAQs para responder
5. Si no encuentras una respuesta adecuada, deriva al encargado humano

TONO:
- Profesional y amable
- Conciso y directo
- Empático con las necesidades del cliente

REGLAS ESPECIALES:
- Para consultas sobre alergias: Derivar siempre a humano por seguridad
- Para grupos grandes (11+ personas): Derivar al encargado
- Para cachopo sin gluten: Mencionar requisito de 24 horas de aviso
- Para eventos: Derivar al encargado
```

### Anexo C: Diagrama de Flujo de Decisiones

```
INICIO: Cliente llama
    ↓
¿Es una reserva?
    ↓ Sí → Flujo de Reserva
    ↓ No
¿Es una consulta FAQ?
    ↓ Sí → Buscar FAQ más relevante
    ↓        ↓
    ↓        ¿Confianza > 0.85?
    ↓        ↓ Sí → Responder con FAQ
    ↓        ↓ No → Derivar a humano
    ↓
¿Es otra consulta?
    ↓ Sí → Derivar a humano
    ↓ No → Pedir clarificación
```

---

## Conclusión

Esta base de conocimiento proporciona una estructura completa para que el agente de voz VAPI pueda responder eficientemente a las consultas más frecuentes de los clientes de En Las Nubes Restobar.

### Próximos Pasos

1. **Configurar campos específicos** del restaurante (horarios, precios, servicios)
2. **Implementar endpoint en n8n** para consulta de FAQs
3. **Integrar con VAPI** usando embeddings de OpenAI
4. **Probar en producción** con llamadas reales
5. **Monitorear métricas** y ajustar según feedback

### Contacto

Para preguntas o sugerencias sobre esta base de conocimiento, contactar al equipo técnico del proyecto.

---

**Documento Version**: 1.0  
**Última Actualización**: 2025-12-25  
**Estado**: Activo
