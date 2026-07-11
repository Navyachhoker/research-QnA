// src/components/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user, ready } = useAuth()
  if (!ready) return null                          // wait for localStorage check
  if (!user)  return <Navigate to="/login" replace />
  return children
}