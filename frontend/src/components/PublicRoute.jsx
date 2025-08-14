import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl text-white">⏳</span>
          </div>
          <p>Cargando...</p>
        </div>
      </div>
    );
  }

  // Si  está autenticado, redirigir al dashboard 
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return children;
};

export default PublicRoute;
