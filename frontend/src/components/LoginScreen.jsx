import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const LoginScreen = () => {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [ loading, setLoading ] = useState(false);
    const { login } = useAuth();
    const  navidate = useNavigate();

    const handleSubmit =async (e) => {
      e.preventDefault()
      setLoading(true);
      
      try{
           await login ( email, password);
           navidate()

      }catch(error){
        console.error("error", error);
        alert ('error al inciar sesion: ${ error.message} ');
      }finally{
        setLoading(false)
      }
 

    }

  return (
    <div className="min-h-screen bg-pink-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl text-white">🎵</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Ecos Music</h1>
          <p className="text-gray-600">Inicia sesión</p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
              placeholder="tu@email.com"
              value={email}
              onChange={ (e) =>setEmail(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña
            </label>
            <input
              type="password"
              id="password"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
              placeholder="********"
              value={password}
              onChange={ (e) =>setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="w-full bg-pink-500 text-white py-2 px-4 rounded-md hover:bg-pink-600 font-medium disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Iniciando sesión..." : "Iniciar Sesión"}
          </button>
        </form>

        {/* Link de registro */}
        <p className="text-center text-sm text-gray-600 mt-4">
          ¿No tienes cuenta?{" "}
          <Link to="/signup" className="text-pink-500 hover:text-pink-600">
            Regístrate
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginScreen;
