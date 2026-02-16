/**
 * Custom Testing Utilities
 *
 * Provides custom render functions and helpers for testing React components
 * with all necessary providers (QueryClient, AuthContext, etc.)
 */

import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../src/contexts/AuthContext';

// ============================================================================
// QUERY CLIENT SETUP
// ============================================================================

/**
 * Creates a fresh QueryClient instance for each test
 * Disables retries and logging to keep tests fast and clean
 */
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Disable retries in tests
        cacheTime: Infinity, // Keep cache during tests
        staleTime: Infinity, // Don't refetch during tests
      },
      mutations: {
        retry: false, // Disable retries in tests
      },
    },
    logger: {
      log: () => {},
      warn: () => {},
      error: () => {},
    },
  });
}

// ============================================================================
// CUSTOM RENDER FUNCTIONS
// ============================================================================

/**
 * Custom render function that wraps components with QueryClientProvider
 * Use this for components that use TanStack Query hooks
 */
export function renderWithQueryClient(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  const queryClient = createTestQueryClient();

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...options }),
    queryClient,
  };
}

/**
 * Custom render function that wraps components with AuthProvider
 * Use this for components that need authentication context
 */
export function renderWithAuth(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  return render(ui, { wrapper: Wrapper, ...options });
}

/**
 * Custom render function that wraps components with ALL providers
 * This is the most common render function - use it by default
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  const queryClient = createTestQueryClient();

  const AllProviders = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );

  return {
    ...render(ui, { wrapper: AllProviders, ...options }),
    queryClient,
  };
}

// ============================================================================
// TESTING HELPERS
// ============================================================================

/**
 * Waits for all loading states to finish
 * Useful after triggering actions that cause loading spinners
 */
export async function waitForLoadingToFinish() {
  const { waitFor } = await import('@testing-library/react');
  await waitFor(() => {
    const loadingSpinners = document.querySelectorAll('[role="status"]');
    const loadingTexts = Array.from(document.querySelectorAll('*')).filter(
      (el) => el.textContent?.includes('Cargando') || el.textContent?.includes('Loading')
    );
    expect(loadingSpinners.length + loadingTexts.length).toBe(0);
  });
}

/**
 * Helper to create a mock authenticated user
 */
export const mockAuthUser = {
  username: 'admin',
  email: 'admin@enlasnubes.com',
  role: 'admin' as const,
  token: 'mock-jwt-token-12345',
};

/**
 * Helper to create a mock unauthenticated state
 */
export const mockUnauthenticatedState = {
  isAuthenticated: false,
  user: null,
  token: null,
  login: vi.fn(),
  logout: vi.fn(),
};

/**
 * Helper to create a mock authenticated state
 */
export const mockAuthenticatedState = {
  isAuthenticated: true,
  user: mockAuthUser,
  token: mockAuthUser.token,
  login: vi.fn(),
  logout: vi.fn(),
};

/**
 * Clears all query caches - useful between tests
 */
export function clearAllQueryCaches() {
  const queryClient = createTestQueryClient();
  queryClient.clear();
}

/**
 * Mock fetch responses for API testing
 * Usage: mockFetchResponse({ data: [...] })
 */
export function mockFetchResponse(response: any) {
  (global.fetch as any).mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: async () => response,
  });
}

/**
 * Mock fetch error for API error testing
 * Usage: mockFetchError(404, 'Not Found')
 */
export function mockFetchError(status: number, message: string) {
  (global.fetch as any).mockResolvedValueOnce({
    ok: false,
    status,
    statusText: message,
    json: async () => ({ error: message }),
  });
}

/**
 * Helper to wait for an element to be removed
 * Useful for testing loading states and modal closures
 */
export async function waitForElementToBeRemoved(element: HTMLElement) {
  const { waitFor } = await import('@testing-library/react');
  await waitFor(() => {
    expect(document.body.contains(element)).toBe(false);
  });
}

/**
 * Simulates a delay (useful for testing loading states)
 */
export function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ============================================================================
// RE-EXPORT EVERYTHING FROM TESTING LIBRARY
// ============================================================================

export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';

// Override the default render with our custom one
export { renderWithProviders as render };
