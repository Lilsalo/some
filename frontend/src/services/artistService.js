import { API_BASE_URL, handleResponse } from './api.js';
import { authService } from './authService.js';

const getArtists = async () => {
  const response = await fetch(`${API_BASE_URL}/artists`);
  return handleResponse(response);
};

const createArtist = async (artist) => {
  const response = await fetch(`${API_BASE_URL}/artists/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authService.getToken()}`,
    },
    body: JSON.stringify(artist),
  });
  return handleResponse(response);
};

const updateArtist = async (id, artist) => {
  const response = await fetch(`${API_BASE_URL}/artists/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authService.getToken()}`,
    },
    body: JSON.stringify(artist),
  });
  return handleResponse(response);
};

const deleteArtist = async (id) => {
  const response = await fetch(`${API_BASE_URL}/artists/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${authService.getToken()}`,
    },
  });
  return handleResponse(response);
};

const getGenres = async () => {
  const response = await fetch(`${API_BASE_URL}/genres`);
  return handleResponse(response);
};

export const artistService = {
  getArtists,
  createArtist,
  updateArtist,
  deleteArtist,
  getGenres,
};
