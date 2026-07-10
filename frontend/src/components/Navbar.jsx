// src/components/Navbar.jsx
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/',        label: 'Upload'  },
  { to: '/ask',     label: 'Ask'     },
  { to: '/analyze', label: 'Analyze' },
  { to: '/papers',  label: 'Papers'  },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate         = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <nav className="border-b border-surface-border bg-surface px-6 py-3 flex items-center justify-between">
      {/* Logo + links */}
      <div className="flex items-center gap-6">
        <span className="text-sm font-semibold text-accent-light tracking-tight">
          ResearchGPT
        </span>
        <div className="flex items-center gap-1">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end
              className={({ isActive }) =>
                `text-xs px-3 py-1.5 rounded-md transition-colors ${
                  isActive
                    ? 'bg-accent-bg text-accent-light'
                    : 'text-ink-secondary hover:text-ink-DEFAULT hover:bg-surface-raised'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div>

      {/* User info */}
      {user && (
        <div className="flex items-center gap-3">
          <span className="text-xs text-ink-muted">{user.email}</span>
          <button
            onClick={handleLogout}
            className="text-xs text-ink-secondary border border-surface-border px-3 py-1.5 rounded-md hover:text-ink-DEFAULT hover:bg-surface-raised transition-colors"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  )
}