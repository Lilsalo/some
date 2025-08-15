// Configuración base de la API
const API_BASE_URL = 'https://ecos-api-production.up.railway.app';

// Función helper para manejar respuestas de la API
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message =
      errorData.message ||
      errorData.detail ||
      `Error ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }
  return response.json();
};


export { API_BASE_URL,  handleResponse };
 