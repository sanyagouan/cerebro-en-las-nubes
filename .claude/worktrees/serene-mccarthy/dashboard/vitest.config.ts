import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

/**
 * Configuración de Vitest para testing unitario y de integración
 * 
 * Testing del Dashboard de En Las Nubes Restobar:
 * - Tests unitarios de componentes React
 * - Tests de validación de formularios (ReservaForm)
 * - Tests de máquina de estados (ReservaDetalle)
 * - Tests de integración con TanStack Query mutations
 * - Coverage objetivo: >70%
 */
export default defineConfig({
  plugins: [react()],
  
  test: {
    // Habilitar APIs de testing globales (describe, it, expect, vi)
    globals: true,
    
    // Entorno de testing: jsdom simula el DOM del navegador
    environment: 'jsdom',
    
    // Archivo de setup ejecutado antes de cada test
    setupFiles: './tests/setup.ts',
    
    // Habilitar procesamiento de CSS en tests
    css: true,
    
    // Configuración de coverage (objetivo: >70%)
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      
      // Directorios/archivos a incluir en coverage
      include: ['src/**/*.{ts,tsx}'],
      
      // Excluir de coverage
      exclude: [
        'node_modules/',
        'tests/',
        'src/**/*.d.ts',
        'src/main.tsx',
        'src/vite-env.d.ts',
      ],
      
      // Umbrales de coverage mínimo
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70,
      },
      
      // Reportes en directorio coverage/
      reportsDirectory: './coverage',
    },
    
    // Timeouts
    testTimeout: 10000, // 10 segundos por test
    hookTimeout: 10000, // 10 segundos para hooks (beforeEach, afterEach)
    
    // Configuración de reporters
    reporters: ['default', 'html'],
    outputFile: {
      html: './vitest-report/index.html',
    },
    
    // Configuración de watch mode
    watch: false, // Desactivado por defecto (usar --watch en CLI)
    
    // Isolate: cada test se ejecuta en su propio entorno aislado
    isolate: true,
    
    // Pool: usar threads para mejor performance
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },
  },
  
  // Resolver aliases para imports
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@contexts': path.resolve(__dirname, './src/contexts'),
      '@config': path.resolve(__dirname, './src/config'),
    },
  },
});
