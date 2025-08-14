import './App.css'

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from 'react-router-dom'


import Dashboard from './components/Dashboard'
import LoginScreen from './components/LoginScreen'

import ProtectedRoute from './components/ProtectedRoute'
import PublicRoute from './components/PublicRoute'
import { AuthProvider } from './context/AuthContext'

function App() {

  return (
  <AuthProvider>
    <Router>
      <div className="App">
        <Routes>
          
          <Route
            path='/login'
            element={
              <PublicRoute>
                <LoginScreen />
              </PublicRoute>
            }
          />

          <Route
            path='/dashboard'
            element={
               <ProtectedRoute>
                 <Dashboard />
               </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  </AuthProvider>
)

}

export default App
