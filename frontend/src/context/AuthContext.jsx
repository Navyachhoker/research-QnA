// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]   = useState(null)    // {email, token}
  const [ready, setReady] = useState(false)   // true once we've checked localStorage

  useEffect(() => {
    const stored = localStorage.getItem('rg_user')
    if (stored) setUser(JSON.parse(stored))
    setReady(true)
  }, [])

  const login = (email, token) => {
    const u = { email, token }
    setUser(u)
    localStorage.setItem('rg_user', JSON.stringify(u))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('rg_user')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, ready }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)