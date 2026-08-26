// API utility functions

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function fetchAPI(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Trip APIs
export const createTrip = (name) => 
  fetchAPI('/trips', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });

export const getTrip = (tripId) => 
  fetchAPI(`/trips/${tripId}`);

// Member APIs
export const addMember = (tripId, name) =>
  fetchAPI(`/trips/${tripId}/members`, {
    method: 'POST',
    body: JSON.stringify({ name }),
  });

export const listMembers = (tripId) =>
  fetchAPI(`/trips/${tripId}/members`);

export const deleteMember = (tripId, memberId) =>
  fetchAPI(`/trips/${tripId}/members/${memberId}`, {
    method: 'DELETE',
  });

// Expense APIs
export const addExpense = (tripId, expenseData) =>
  fetchAPI(`/trips/${tripId}/expenses`, {
    method: 'POST',
    body: JSON.stringify(expenseData),
  });

export const listExpenses = (tripId) =>
  fetchAPI(`/trips/${tripId}/expenses`);

// Settlement API
export const getSettlement = (tripId) =>
  fetchAPI(`/trips/${tripId}/settlement`);

// Sheet APIs
export const getSheet = (tripId) =>
  fetchAPI(`/trips/${tripId}/sheet`);

export const getSheetPdfUrl = (tripId) =>
  `${API_BASE}/trips/${tripId}/sheet/pdf`;
