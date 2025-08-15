// Validadores para formularios

/**
 * Valida el formato de email según el patrón del backend
 * @param {string} email - Email a validar
 * @returns {boolean} - True si es válido, false si no
 */
export const isValidEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
};

/**
 * Valida contraseña según los criterios del backend
 * @param {string} password - Contraseña a validar
 * @returns {object} - Objeto con isValid (boolean) y message (string)
 */
export const validatePassword = (password) => {
    // Validar longitud
    if (password.length < 8) {
        return {
            isValid: false,
            message: 'La contraseña debe tener entre 8 y 64 caracteres'
        };
    }
    
    if (password.length > 64) {
        return {
            isValid: false,
            message: 'La contraseña debe tener entre 8 y 64 caracteres'
        };
    }
    
    // Validar que contenga al menos una mayúscula
    if (!/[A-Z]/.test(password)) {
        return {
            isValid: false,
            message: 'La contraseña debe contener al menos una letra mayúscula'
        };
    }
    
    // Validar que contenga al menos un número
    if (!/\d/.test(password)) {
        return {
            isValid: false,
            message: 'La contraseña debe contener al menos un número'
        };
    }
    
    // Validar que contenga al menos un carácter especial
    if (!/[@$!%*?&]/.test(password)) {
        return {
            isValid: false,
            message: 'La contraseña debe contener al menos un carácter especial (@$!%*?&)'
        };
    }
    
    return {
        isValid: true,
        message: 'Contraseña válida'
    };
};

/**
 * Obtiene indicadores visuales de la fortaleza de la contraseña
 * @param {string} password - Contraseña a evaluar
 * @returns {object} - Objeto con criterios y su estado
 */
export const getPasswordStrength = (password) => {
    return {
        hasMinLength: password.length >= 8,
        hasMaxLength: password.length <= 64,
        hasUppercase: /[A-Z]/.test(password),
        hasNumber: /\d/.test(password),
        hasSpecialChar: /[@$!%*?&]/.test(password),
        isValidLength: password.length >= 8 && password.length <= 64
    };
};