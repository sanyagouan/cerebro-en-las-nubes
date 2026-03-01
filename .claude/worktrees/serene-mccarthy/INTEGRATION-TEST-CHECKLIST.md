# Integration Testing Checklist - Reservation Management

## ✅ Completed Implementation

### Components
- [x] Reservas.tsx - Main reservations list with filters and actions
- [x] ReservaForm.tsx - Create/Edit modal form
- [x] ReservaDetalle.tsx - Reservation detail modal with status actions
- [x] useReservations.ts - React Query hooks for API integration

### Features Implemented
- [x] List reservations with pagination
- [x] Filter by status (Pendiente, Confirmada, Cancelada, Completada)
- [x] Search by name/phone
- [x] Create new reservation
- [x] Edit existing reservation
- [x] Status change actions (Confirm, Seat, Complete, Cancel)
- [x] Optimistic UI updates
- [x] Error handling with console logging
- [x] Loading states during mutations

---

## 🧪 Testing Tasks

### 1. Visual/UI Testing (Frontend Only)
**Prerequisites:** Backend API must be running at configured endpoint

#### Test 1.1: Load Reservations List
- [ ] Start dev server: `cd dashboard && npm run dev`
- [ ] Navigate to Reservations page
- [ ] Verify loading spinner appears
- [ ] Verify table loads with reservation data
- [ ] Check all columns display correctly: Cliente, Fecha y Hora, Personas, Mesa, Estado, Origen, Acciones

#### Test 1.2: Filter Functionality
- [ ] Test "Todos los estados" filter - shows all
- [ ] Test "Pendiente" filter - shows only pending
- [ ] Test "Confirmada" filter - shows only confirmed
- [ ] Test "Cancelada" filter - shows only cancelled
- [ ] Test "Completada" filter - shows only completed

#### Test 1.3: Search Functionality
- [ ] Search by customer name (partial match)
- [ ] Search by phone number (partial match)
- [ ] Verify empty state when no matches found

#### Test 1.4: Create Reservation
- [ ] Click "Nueva Reserva" button
- [ ] Verify modal opens
- [ ] Fill all required fields: nombre, telefono, fecha, hora, pax
- [ ] Submit form
- [ ] Verify loading state during submission
- [ ] Verify modal closes on success
- [ ] Verify new reservation appears in list
- [ ] Check console for any errors

#### Test 1.5: Edit Reservation
- [ ] Click Edit icon (pencil) on a reservation
- [ ] Verify modal opens with pre-filled data
- [ ] Modify some fields
- [ ] Submit form
- [ ] Verify loading state during submission
- [ ] Verify modal closes on success
- [ ] Verify changes reflected in list
- [ ] Check console for any errors

#### Test 1.6: View Reservation Details
- [ ] Click on a reservation row
- [ ] Verify detail modal opens
- [ ] Verify all information displays correctly
- [ ] Verify status badge color matches status
- [ ] Close modal

#### Test 1.7: Status Change Actions - Confirm
- [ ] Find a "Pendiente" reservation
- [ ] Click green checkmark (Confirm)
- [ ] Verify optimistic update (status changes immediately)
- [ ] Wait for API response
- [ ] Verify status persists as "Confirmada"
- [ ] Check console for any errors

#### Test 1.8: Status Change Actions - Seat
- [ ] Find a "Confirmada" reservation
- [ ] Click on row to open detail modal
- [ ] Click "Sentar" button
- [ ] Verify status changes to "Sentada"
- [ ] Close modal
- [ ] Verify status persists in list

#### Test 1.9: Status Change Actions - Complete
- [ ] Find a "Sentada" reservation
- [ ] Click on row to open detail modal
- [ ] Click "Completar" button
- [ ] Verify status changes to "Completada"
- [ ] Close modal
- [ ] Verify status persists in list

#### Test 1.10: Status Change Actions - Cancel
- [ ] Find a non-cancelled reservation
- [ ] Click red X icon (Cancel)
- [ ] Verify optimistic update (status changes immediately)
- [ ] Wait for API response
- [ ] Verify status persists as "Cancelada"
- [ ] Check console for any errors

#### Test 1.11: Error Handling
- [ ] Stop backend API
- [ ] Try to create a new reservation
- [ ] Verify error message in console
- [ ] Verify form stays open
- [ ] Restart backend API
- [ ] Try again - should work

#### Test 1.12: Disabled States
- [ ] Click Confirm on already "Confirmada" reservation - button should be disabled
- [ ] Click Cancel on already "Cancelada" reservation - button should be disabled
- [ ] Start a mutation (create/edit)
- [ ] Verify all action buttons disable during mutation
- [ ] Wait for mutation to complete
- [ ] Verify buttons re-enable

---

### 2. API Integration Testing (Backend Required)

#### Test 2.1: Backend Health Check
- [ ] Backend running at: `http://localhost:8000` (or configured API_BASE_URL)
- [ ] Check `/health` endpoint returns 200
- [ ] Check `/docs` for Swagger UI

#### Test 2.2: GET /api/mobile/reservations
- [ ] Verify endpoint returns paginated data
- [ ] Check response structure matches `PaginatedReservations` type
- [ ] Test with filters: `?estado=Pendiente`
- [ ] Test with offset/limit pagination
- [ ] Verify field mapping: customer_name → nombre, phone → telefono, etc.

#### Test 2.3: POST /api/mobile/reservations (Create)
- [ ] Send valid reservation data
- [ ] Verify 201 response with created reservation
- [ ] Check reservation appears in GET list
- [ ] Test validation: missing required fields should error
- [ ] Test validation: invalid phone format should error

#### Test 2.4: PUT /api/mobile/reservations/{id} (Update)
- [ ] Update existing reservation
- [ ] Verify 200 response with updated data
- [ ] Check changes reflected in GET list
- [ ] Test validation: invalid data should error

#### Test 2.5: PUT /api/mobile/reservations/{id}/status
- [ ] Change status from Pendiente → Confirmada
- [ ] Change status from Confirmada → Sentada
- [ ] Change status from Sentada → Completada
- [ ] Change status to Cancelada
- [ ] Verify each returns 200
- [ ] Verify status persists in database

#### Test 2.6: Error Scenarios
- [ ] Test non-existent reservation ID (404 expected)
- [ ] Test malformed request body (400 expected)
- [ ] Test unauthorized access if auth implemented

---

### 3. React Query Cache Testing

#### Test 3.1: Automatic Cache Invalidation
- [ ] Open two browser windows side by side
- [ ] Create reservation in window 1
- [ ] Wait for mutation to complete
- [ ] Manually refresh window 2
- [ ] Verify new reservation appears (cache invalidated)

#### Test 3.2: Optimistic Updates
- [ ] Click Confirm on a reservation
- [ ] Watch status change IMMEDIATELY (optimistic)
- [ ] Wait for API response
- [ ] Verify status doesn't revert (real update matches optimistic)

#### Test 3.3: Error Rollback
- [ ] Stop backend
- [ ] Try to confirm a reservation (will fail)
- [ ] Verify optimistic update occurs
- [ ] Wait for error
- [ ] Verify status rolls back to original (error rollback works)

---

### 4. Form Validation Testing

#### Test 4.1: ReservaForm Validation (if implemented)
- [ ] Open create form
- [ ] Submit without filling any fields
- [ ] Verify validation errors appear
- [ ] Fill required fields one by one
- [ ] Verify errors clear as fields are filled
- [ ] Test phone number format validation
- [ ] Test date/time validation (past dates, invalid times)

---

### 5. Network Testing

#### Test 5.1: Slow Network
- [ ] Open Chrome DevTools → Network tab
- [ ] Throttle to "Slow 3G"
- [ ] Create a reservation
- [ ] Verify loading spinner shows
- [ ] Wait for completion
- [ ] Verify success feedback

#### Test 5.2: Offline Mode
- [ ] Disconnect network
- [ ] Try to create reservation
- [ ] Verify error handling (console message or toast if implemented)
- [ ] Reconnect network
- [ ] Retry - should work

---

## 📋 Test Results Summary

**Date Tested:** _________________
**Tester:** _________________
**Backend Version:** _________________
**Frontend Version:** _________________

### Pass/Fail Summary
- Visual/UI Testing: ____ / 12 passed
- API Integration: ____ / 6 passed
- React Query Cache: ____ / 3 passed
- Form Validation: ____ / 1 passed
- Network Testing: ____ / 2 passed

**Total: ____ / 24 tests passed**

### Issues Found
1. 
2. 
3. 

### Notes
- 
- 
- 

---

## 🚀 Next Steps After Testing

If all tests pass:
- [x] Mark todo task "Test reservation management functionality" as COMPLETED
- [ ] Move to next phase: WebSocket Integration (Days 21-22)
- [ ] Or: Add toast notifications for better UX feedback
- [ ] Or: Implement MesaForm integration for table management

If issues found:
- [ ] Document bugs in GitHub issues or project tracker
- [ ] Prioritize by severity
- [ ] Fix critical bugs before proceeding
- [ ] Re-test after fixes
