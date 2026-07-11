// src/pages/RegisterPage.jsx
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register as registerApi } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const { login }               = useAuth()
  const navigate                = useNavigate()
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  const handleSubmit = async () => {
    setLoading(true); setError('')
    try {
      const { data } = await registerApi(email, password)
      login(data.email, data.access_token)
      navigate('/')
    } catch (e) {
      setError(e.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  const inputClass = "w-full bg-surface-raised border border-surface-border rounded-lg px-3 py-2.5 text-sm text-ink-DEFAULT placeholder:text-ink-muted focus:outline-none focus:border-accent-border transition-colors"

  return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-xl font-semibold text-accent-light">ResearchGPT</span>
          <p className="text-xs text-ink-muted mt-1">Create your account</p>
        </div>

        <div className="bg-surface border border-surface-border rounded-2xl p-6 space-y-4">
          <div>
            <label className="block text-xs font-medium text-ink-muted mb-1.5">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" className={inputClass} />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-muted mb-1.5">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSubmit()} placeholder="Min. 6 characters" className={inputClass} />
          </div>

          {error && (
            <p className="text-xs text-red-400 bg-red-950/30 border border-red-900/40 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-accent text-surface-base py-2.5 rounded-xl text-sm font-medium hover:bg-accent-light disabled:opacity-40 transition-colors"
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </div>

        <p className="text-center text-xs text-ink-muted mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-accent-light hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}