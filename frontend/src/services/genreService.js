import { API_BASE_URL, handleResponse } from './api.js';
import { authService } from './authService.js';

const authHeaders = () => {
  const token = authService.getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const getAll = async () => {
  const res = await fetch(`${API_BASE_URL}/genres`);
  return handleResponse(res);
};

const create = async (genre) => {
  const res = await fetch(`${API_BASE_URL}/genres`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(genre),
  });
  return handleResponse(res);
};

const update = async (id, genre) => {
  const res = await fetch(`${API_BASE_URL}/genres/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(genre),
  });
  return handleResponse(res);
};

const remove = async (id) => {
  const res = await fetch(`${API_BASE_URL}/genres/${id}`, {
    method: 'DELETE',
    headers: { ...authHeaders() },
  });
  return handleResponse(res);
};

export const genreService = { getAll, create, update, remove };
