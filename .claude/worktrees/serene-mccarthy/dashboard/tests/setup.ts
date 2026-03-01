/**
 * Global Test Setup Configuration
 *
 * This file is loaded before all tests (referenced in vitest.config.ts)
 * Sets up global mocks, matchers, and test environment configuration
 */

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeAll, vi } from 'vitest';

// ============================================================================
// AUTOMATIC CLEANUP
// ============================================================================

// Cleanup after each test automatically
afterEach(() => {
  cleanup();
});

// ============================================================================
// GLOBAL MOCKS
// ============================================================================

// Mock window.matchMedia (required for responsive components)
beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // Deprecated
      removeListener: vi.fn(), // Deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
});

// Mock IntersectionObserver (required for lazy loading, virtual scrolling)
beforeAll(() => {
  global.IntersectionObserver = class IntersectionObserver {
    constructor() {}
    disconnect() {}
    observe() {}
    takeRecords() {
      return [];
    }
    unobserve() {}
  } as any;
});

// Mock ResizeObserver (required for responsive components)
beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    constructor() {}
    disconnect() {}
    observe() {}
    unobserve() {}
  } as any;
});

// Mock localStorage
beforeAll(() => {
  const localStorageMock = (() => {
    let store: Record<string, string> = {};

    return {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value.toString();
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        store = {};
      },
      get length() {
        return Object.keys(store).length;
      },
      key: (index: number) => {
        const keys = Object.keys(store);
        return keys[index] || null;
      },
    };
  })();

  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  });
});

// Mock sessionStorage
beforeAll(() => {
  const sessionStorageMock = (() => {
    let store: Record<string, string> = {};

    return {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value.toString();
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        store = {};
      },
      get length() {
        return Object.keys(store).length;
      },
      key: (index: number) => {
        const keys = Object.keys(store);
        return keys[index] || null;
      },
    };
  })();

  Object.defineProperty(window, 'sessionStorage', {
    value: sessionStorageMock,
  });
});

// Mock fetch API (for API testing)
beforeAll(() => {
  global.fetch = vi.fn();
});

// ============================================================================
// MOCK DATE/TIME FOR DETERMINISTIC TESTS
// ============================================================================

// Set a consistent date for tests: 2024-01-15 14:30:00 (Monday, lunch service)
beforeAll(() => {
  const mockDate = new Date('2024-01-15T14:30:00.000Z');
  vi.setSystemTime(mockDate);
});

// ============================================================================
// CONSOLE FILTERING
// ============================================================================

// Filter out expected console warnings/errors in test environment
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    // Ignore React Testing Library act() warnings (they're usually false positives)
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: An update to') &&
      args[0].includes('was not wrapped in act')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };

  console.warn = (...args: any[]) => {
    // Ignore TanStack Query dev tools warnings in tests
    if (
      typeof args[0] === 'string' &&
      args[0].includes('React Query Devtools')
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

// ============================================================================
// TEST ENVIRONMENT VARIABLES
// ============================================================================

// Set test-specific environment variables
process.env.NODE_ENV = 'test';
process.env.VITE_API_URL = 'http://localhost:8000/api';
process.env.VITE_WS_URL = 'ws://localhost:8000/ws';

// ============================================================================
// CUSTOM MATCHERS (if needed in the future)
// ============================================================================

// Add custom matchers here if needed
// Example:
// expect.extend({
//   toBeValidReservation(received) {
//     // Custom matcher logic
//   },
// });
