# Dashboard - En Las Nubes Restobar

Dashboard de administración para el sistema de reservas del restaurante "En Las Nubes".

## Características

- 📊 **Dashboard Principal**: Métricas en tiempo real de reservas, ocupación y alertas
- 📅 **Gestión de Reservas**: Lista completa con filtros, búsqueda y acciones
- 🪑 **Control de Mesas**: Visualización del estado de todas las mesas (interior/terraza)
- 👥 **Clientes**: Base de datos de clientes (próximamente)
- ⚙️ **Configuración**: Ajustes del sistema (próximamente)

## Tecnologías

- React 18 + TypeScript
- Tailwind CSS
- Vite
- Lucide React (iconos)
- Recharts (gráficos - próximamente)

## Instalación

```bash
cd dashboard
npm install
```

## Desarrollo

```bash
npm run dev
```

El dashboard estará disponible en http://localhost:3000

## Build para Producción

```bash
npm run build
```

Los archivos estáticos se generarán en la carpeta `dist/`.

## Estructura

```
dashboard/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx    # Vista principal con métricas
│   │   ├── Reservas.tsx     # Lista y gestión de reservas
│   │   └── Mesas.tsx        # Control de mesas
│   ├── types.ts             # Tipos TypeScript
│   ├── App.tsx              # Componente principal
│   └── main.tsx             # Entry point
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

## Conexión con Backend

Por defecto, el dashboard se conecta a la API en `http://localhost:8000`.
Ajusta la configuración en `vite.config.ts` si es necesario.

## Próximas Mejoras

- [ ] Conexión real con API de Airtable
- [ ] Autenticación de usuarios
- [ ] Notificaciones en tiempo real (WebSockets)
- [ ] Gráficos de tendencias
- [ ] Exportación de reportes
- [ ] Modo oscuro
