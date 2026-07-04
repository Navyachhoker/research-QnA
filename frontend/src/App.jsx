// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute  from './components/ProtectedRoute'
import Navbar          from './components/Navbar'
import UploadPage      from './pages/UploadPage'
import AskPage         from './pages/AskPage'
import AnalyzePage     from './pages/AnalyzePage'
import PapersPage      from './pages/PapersPage'
import LoginPage       from './pages/LoginPage'
import RegisterPage    from './pages/RegisterPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login"    element={<LoginPage />}    />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes — wrapped in Navbar */}
          <Route path="/*" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Navbar />
                <Routes>
                  <Route path="/"        element={<UploadPage />}  />
                  <Route path="/ask"     element={<AskPage />}     />
                  <Route path="/analyze" element={<AnalyzePage />} />
                  <Route path="/papers"  element={<PapersPage />}  />
                </Routes>
              </div>
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}