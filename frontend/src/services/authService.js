import { API_BASE_URL, handleResponse } from "./api.js";

const saveSession = (token, extras = {}) => {
  localStorage.setItem("authToken", token);

  // Intentar leer nombres desde extras primero
  let userInfo = {
    email: extras.email || "",
    firstname: extras.firstname || "",
    lastname: extras.lastname || "",
  };

  // Si faltan nombres, intentar decodificar el JWT
  if (!userInfo.firstname || !userInfo.lastname) {
    try {
      const payload = decodeToken(token);
      userInfo = {
        email: userInfo.email || payload.email || "",
        firstname: userInfo.firstname || payload.firstname || payload.name || "",
        lastname: userInfo.lastname || payload.lastname || "",
      };
    } catch {
      // si el token no decodifica, mantenemos lo que tengamos
    }
  }

  localStorage.setItem("userInfo", JSON.stringify(userInfo));
};

export const authService = {
  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      let message = "Error al iniciar sesión. Intenta nuevamente.";
      try {
        const err = await response.json();
        if (err?.detail || err?.message) message = err.detail || err.message;
      } catch {}
      if (response.status === 401) {
        throw new Error("Credenciales inválidas. Verifica tu email y contraseña.");
      }
      throw new Error(message);
    }

    const data = await response.json();

    // Soportar distintas formas de respuesta
    const token = data.access_token || data.idToken;
    if (!token) throw new Error("No se recibió token de autenticación.");

    saveSession(token, {
      email,
      firstname: data.firstname,
      lastname: data.lastname
    });

    return data;
  },

  register: async (name, lastname, email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, lastname, email, password })
      });
      const data = await handleResponse(response);
      return data;
    } catch (error) {
      console.error("Error en registro:", error);
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userInfo");
  },

  isAuthenticated: () => {
    const token = localStorage.getItem("authToken");
    if (!token) return false;
    try {
      const payload = decodeToken(token);
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  },

  getCurrentUser: () => {
    try {
      const raw = localStorage.getItem("userInfo");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  getToken: () => localStorage.getItem("authToken")
};

const decodeToken = (token) => {
  const base64Url = token.split(".")[1];
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split("")
      .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  );
  return JSON.parse(jsonPayload);
};
