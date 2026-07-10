// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider }  from './context/AuthContext'
import ProtectedRoute    from './components/ProtectedRoute'
import Navbar            from './components/Navbar'
import UploadPage        from './pages/UploadPage'
import AskPage           from './pages/AskPage'
import AnalyzePage       from './pages/AnalyzePage'
import PapersPage        from './pages/PapersPage'
import LoginPage         from './pages/LoginPage'
import RegisterPage      from './pages/RegisterPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        {/* Dark wrapper — guarantees background even before Tailwind loads */}
        <div style={{ backgroundColor: '#111110', minHeight: '100vh' }}>
          <Routes>
            <Route path="/login"    element={<LoginPage />}    />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/*" element={
              <ProtectedRoute>
                <div style={{ backgroundColor: '#111110', minHeight: '100vh' }}>
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
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}