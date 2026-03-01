/**
 * Unit Tests: ReservaForm Component
 * 
 * Tests comprehensive validation logic for the reservation form:
 * - Spanish phone number validation
 * - Service hours validation (12:00-23:59)
 * - Party size validation (1-20 people)
 * - Date validation (no past dates)
 * - Required field validation
 * - Form submission behavior
 * - Error handling and display
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ReservaForm from '../../src/components/ReservaForm';
import {
  mockReservations,
  validSpanishPhones,
  invalidSpanishPhones,
  validServiceHours,
  invalidServiceHours,
  validPartySizes,
  invalidPartySizes,
  createMockReservation,
} from '../fixtures/mockData';
import { renderWithProviders } from '../test-utils';

describe('ReservaForm Component', () => {
  const mockOnClose = vi.fn();
  const mockOnSubmit = vi.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    mockOnClose.mockClear();
    mockOnSubmit.mockClear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ============================================================================
  // RENDERING AND INITIAL STATE
  // ============================================================================

  describe('Rendering and Initial State', () => {
    it('should not render when isOpen is false', () => {
      renderWithProviders(
        <ReservaForm
          isOpen={false}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      expect(screen.queryByText('Nueva Reserva')).not.toBeInTheDocument();
    });

    it('should render create mode with correct title', () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      expect(screen.getByText('Nueva Reserva')).toBeInTheDocument();
    });

    it('should render edit mode with correct title and initial data', () => {
      const reservation = mockReservations[0]; // Pendiente reservation

      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="edit"
          initialData={reservation}
        />
      );

      expect(screen.getByText('Editar Reserva')).toBeInTheDocument();
      expect(screen.getByDisplayValue(reservation.nombre)).toBeInTheDocument();
      expect(screen.getByDisplayValue(reservation.telefono)).toBeInTheDocument();
      expect(screen.getByDisplayValue(reservation.fecha)).toBeInTheDocument();
      expect(screen.getByDisplayValue(reservation.hora)).toBeInTheDocument();
    });

    it('should initialize form with default values in create mode', () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Default party size should be 2
      const paxInput = screen.getByLabelText(/Número de Personas/i);
      expect(paxInput).toHaveValue(2);

      // Fecha should default to today
      const today = new Date().toISOString().split('T')[0];
      const fechaInput = screen.getByLabelText(/Fecha/i);
      expect(fechaInput).toHaveValue(today);
    });

    it('should display estado field only in edit mode', () => {
      const { rerender } = renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      expect(screen.queryByLabelText(/Estado/i)).not.toBeInTheDocument();

      rerender(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="edit"
          initialData={mockReservations[0]}
        />
      );

      expect(screen.getByLabelText(/Estado/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // PHONE NUMBER VALIDATION
  // ============================================================================

  describe('Phone Number Validation', () => {
    it('should accept valid Spanish phone formats', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const phoneInput = screen.getByLabelText(/Teléfono/i);

      for (const validPhone of validSpanishPhones) {
        await user.clear(phoneInput);
        await user.type(phoneInput, validPhone);

        // Try to submit to trigger validation
        const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
        await user.click(submitButton);

        // Should NOT show phone error for valid phones
        // (other fields may have errors, but not phone)
        await waitFor(() => {
          const phoneError = screen.queryByText(/Formato de teléfono inválido/i);
          expect(phoneError).not.toBeInTheDocument();
        });
      }
    });

    it('should reject invalid Spanish phone formats', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const phoneInput = screen.getByLabelText(/Teléfono/i);

      for (const invalidPhone of invalidSpanishPhones) {
        await user.clear(phoneInput);
        await user.type(phoneInput, invalidPhone);

        // Blur to trigger validation
        await user.tab();

        // Fill required fields to isolate phone validation
        const nombreInput = screen.getByLabelText(/Nombre Completo/i);
        await user.type(nombreInput, 'Test User');

        const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
        await user.click(submitButton);

        // Should show phone error
        await waitFor(() => {
          expect(screen.getByText(/Formato de teléfono inválido/i)).toBeInTheDocument();
        });
      }
    });

    it('should show error when phone field is empty', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/El teléfono es requerido/i)).toBeInTheDocument();
      });
    });
  });

  // ============================================================================
  // SERVICE HOURS VALIDATION
  // ============================================================================

  describe('Service Hours Validation (12:00-23:59)', () => {
    it('should accept valid service hours', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const horaInput = screen.getByLabelText(/Hora/i);

      for (const validHour of validServiceHours) {
        await user.clear(horaInput);
        await user.type(horaInput, validHour);

        // Try to submit
        const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
        await user.click(submitButton);

        // Should NOT show hour error for valid hours
        await waitFor(() => {
          const hourError = screen.queryByText(/Horario de servicio: 12:00 - 23:59/i);
          expect(hourError).not.toBeInTheDocument();
        });
      }
    });

    it('should reject hours outside service hours', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const horaInput = screen.getByLabelText(/Hora/i);

      for (const invalidHour of invalidServiceHours) {
        await user.clear(horaInput);
        await user.type(horaInput, invalidHour);

        // Fill required fields
        const nombreInput = screen.getByLabelText(/Nombre Completo/i);
        await user.clear(nombreInput);
        await user.type(nombreInput, 'Test User');

        const telefonoInput = screen.getByLabelText(/Teléfono/i);
        await user.clear(telefonoInput);
        await user.type(telefonoInput, '612345678');

        const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
        await user.click(submitButton);

        // Should show hour error
        await waitFor(() => {
          expect(screen.getByText(/Horario de servicio: 12:00 - 23:59/i)).toBeInTheDocument();
        });
      }
    });

    it('should show helper text for service hours', () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      expect(screen.getByText(/Horario de servicio: 12:00 - 23:59/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // PARTY SIZE VALIDATION
  // ============================================================================

  describe('Party Size Validation (1-20 people)', () => {
    it('should accept valid party sizes', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const paxInput = screen.getByLabelText(/Número de Personas/i);

      for (const validSize of validPartySizes) {
        await user.clear(paxInput);
        await user.type(paxInput, validSize.toString());

        // Try to submit
        const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
        await user.click(submitButton);

        // Should NOT show pax error for valid sizes
        await waitFor(() => {
          const paxError = screen.queryByText(/Mínimo 1 persona|Máximo 20 personas/i);
          expect(paxError).not.toBeInTheDocument();
        });
      }
    });

    it('should reject party size less than 1', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const paxInput = screen.getByLabelText(/Número de Personas/i);
      await user.clear(paxInput);
      await user.type(paxInput, '0');

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Mínimo 1 persona/i)).toBeInTheDocument();
      });
    });

    it('should reject party size greater than 20', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const paxInput = screen.getByLabelText(/Número de Personas/i);
      await user.clear(paxInput);
      await user.type(paxInput, '25');

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Máximo 20 personas/i)).toBeInTheDocument();
      });
    });
  });

  // ============================================================================
  // DATE VALIDATION
  // ============================================================================

  describe('Date Validation', () => {
    it('should accept future dates', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const fechaInput = screen.getByLabelText(/Fecha/i);
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().split('T')[0];

      await user.clear(fechaInput);
      await user.type(fechaInput, tomorrowStr);

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      // Should NOT show date error for future dates
      await waitFor(() => {
        const dateError = screen.queryByText(/No se pueden crear reservas en fechas pasadas/i);
        expect(dateError).not.toBeInTheDocument();
      });
    });

    it('should accept today as valid date', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const fechaInput = screen.getByLabelText(/Fecha/i);
      const today = new Date().toISOString().split('T')[0];

      await user.clear(fechaInput);
      await user.type(fechaInput, today);

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      // Should NOT show date error for today
      await waitFor(() => {
        const dateError = screen.queryByText(/No se pueden crear reservas en fechas pasadas/i);
        expect(dateError).not.toBeInTheDocument();
      });
    });

    it('should reject past dates', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const fechaInput = screen.getByLabelText(/Fecha/i);
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayStr = yesterday.toISOString().split('T')[0];

      await user.clear(fechaInput);
      await user.type(fechaInput, yesterdayStr);

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/No se pueden crear reservas en fechas pasadas/i)).toBeInTheDocument();
      });
    });

    it('should show error when date field is empty', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const fechaInput = screen.getByLabelText(/Fecha/i);
      await user.clear(fechaInput);

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/La fecha es requerida/i)).toBeInTheDocument();
      });
    });
  });

  // ============================================================================
  // NOMBRE VALIDATION
  // ============================================================================

  describe('Nombre (Name) Validation', () => {
    it('should accept valid names', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const nombreInput = screen.getByLabelText(/Nombre Completo/i);
      await user.type(nombreInput, 'Juan Pérez García');

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      // Should NOT show nombre error for valid names
      await waitFor(() => {
        const nameError = screen.queryByText(/El nombre es requerido|El nombre debe tener al menos 2 caracteres/i);
        expect(nameError).not.toBeInTheDocument();
      });
    });

    it('should show error when nombre is empty', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/El nombre es requerido/i)).toBeInTheDocument();
      });
    });

    it('should reject names shorter than 2 characters', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const nombreInput = screen.getByLabelText(/Nombre Completo/i);
      await user.type(nombreInput, 'A');

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/El nombre debe tener al menos 2 caracteres/i)).toBeInTheDocument();
      });
    });
  });

  // ============================================================================
  // FORM SUBMISSION
  // ============================================================================

  describe('Form Submission', () => {
    it('should successfully submit with all valid data', async () => {
      mockOnSubmit.mockResolvedValue(undefined);

      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Fill all required fields with valid data
      await user.type(screen.getByLabelText(/Nombre Completo/i), 'María López García');
      await user.type(screen.getByLabelText(/Teléfono/i), '612345678');
      
      const fechaInput = screen.getByLabelText(/Fecha/i);
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      await user.clear(fechaInput);
      await user.type(fechaInput, tomorrow.toISOString().split('T')[0]);

      await user.clear(screen.getByLabelText(/Hora/i));
      await user.type(screen.getByLabelText(/Hora/i), '19:30');

      const paxInput = screen.getByLabelText(/Número de Personas/i);
      await user.clear(paxInput);
      await user.type(paxInput, '4');

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledTimes(1);
        expect(mockOnClose).toHaveBeenCalledTimes(1);
      });
    });

    it('should show loading state during submission', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Fill valid data
      await user.type(screen.getByLabelText(/Nombre Completo/i), 'Test User');
      await user.type(screen.getByLabelText(/Teléfono/i), '612345678');

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      // Should show loading text
      await waitFor(() => {
        expect(screen.getByText(/Guardando.../i)).toBeInTheDocument();
      });

      // Button should be disabled
      expect(submitButton).toBeDisabled();
    });

    it('should not submit when validation fails', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Leave fields empty and try to submit
      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        // Should show multiple validation errors
        expect(screen.getByText(/El nombre es requerido/i)).toBeInTheDocument();
        expect(screen.getByText(/El teléfono es requerido/i)).toBeInTheDocument();
      });

      // onSubmit should NOT have been called
      expect(mockOnSubmit).not.toHaveBeenCalled();
      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it('should include notas in submission data', async () => {
      mockOnSubmit.mockResolvedValue(undefined);

      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Fill required fields
      await user.type(screen.getByLabelText(/Nombre Completo/i), 'Test User');
      await user.type(screen.getByLabelText(/Teléfono/i), '612345678');

      // Add special requests
      const notasInput = screen.getByLabelText(/Solicitudes Especiales/i);
      await user.type(notasInput, 'Mesa cerca de la ventana, alergias a frutos secos');

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            notas: 'Mesa cerca de la ventana, alergias a frutos secos'
          })
        );
      });
    });
  });

  // ============================================================================
  // ERROR HANDLING AND UI FEEDBACK
  // ============================================================================

  describe('Error Handling and UI Feedback', () => {
    it('should clear error when user corrects invalid input', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const telefonoInput = screen.getByLabelText(/Teléfono/i);

      // Enter invalid phone
      await user.type(telefonoInput, '123');
      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      // Error should appear
      await waitFor(() => {
        expect(screen.getByText(/Formato de teléfono inválido/i)).toBeInTheDocument();
      });

      // Correct the phone
      await user.clear(telefonoInput);
      await user.type(telefonoInput, '612345678');

      // Error should disappear
      await waitFor(() => {
        expect(screen.queryByText(/Formato de teléfono inválido/i)).not.toBeInTheDocument();
      });
    });

    it('should display AlertCircle icon with error messages', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      await waitFor(() => {
        // Error messages should be visible
        const errorMessages = screen.getAllByText(/es requerido/i);
        expect(errorMessages.length).toBeGreaterThan(0);

        // Each error should have text-red-600 styling (from AlertCircle wrapper)
        errorMessages.forEach(msg => {
          const parent = msg.closest('.text-red-600');
          expect(parent).toBeInTheDocument();
        });
      });
    });
  });

  // ============================================================================
  // CLOSE BEHAVIOR
  // ============================================================================

  describe('Close Behavior', () => {
    it('should call onClose when cancel button is clicked', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      const cancelButton = screen.getByRole('button', { name: /Cancelar/i });
      await user.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when X button is clicked', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Find X button (it's the button with X icon in header)
      const closeButtons = screen.getAllByRole('button');
      const xButton = closeButtons.find(btn => 
        btn.querySelector('svg') && btn.closest('.border-b')
      );

      expect(xButton).toBeDefined();
      await user.click(xButton!);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when backdrop is clicked', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Find backdrop (it's the div with bg-black/50)
      const backdrop = document.querySelector('.bg-black\\/50');
      expect(backdrop).toBeInTheDocument();

      await user.click(backdrop!);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should close on ESC key press', async () => {
      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      await user.keyboard('{Escape}');

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should not close on ESC when form is submitting', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderWithProviders(
        <ReservaForm
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          mode="create"
        />
      );

      // Fill and submit
      await user.type(screen.getByLabelText(/Nombre Completo/i), 'Test User');
      await user.type(screen.getByLabelText(/Teléfono/i), '612345678');
      
      const submitButton = screen.getByRole('button', { name: /Crear Reserva/i });
      await user.click(submitButton);

      // Try ESC while submitting
      await user.keyboard('{Escape}');

      // Should NOT close
      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });
});
