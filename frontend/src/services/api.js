// Configuración base de la API
const API_BASE_URL = 'https://ecos-api-production.up.railway.app';

// Función helper para manejar respuestas de la API
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
};


export { API_BASE_URL,  handleResponse };
 