// src/components/Navbar.jsx

import { NavLink } from "react-router-dom";
import { useAuth } from '../context/AuthContext'

const navLinks = [
  {
    path: "/",
    label: "Upload",
  },
  {
    path: "/ask",
    label: "Ask",
  },
  {
    path: "/analyze",
    label: "Analyze",
  },
  {
    path: "/papers",
    label: "Papers",
  },
];

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate         = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-md">
      <div className="flex items-center gap-8">
        <span className="font-bold text-lg tracking-tight text-indigo-400">ResearchGPT</span>
        <div className="flex gap-4">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end
              className={({ isActive }) =>
                `text-sm px-3 py-1.5 rounded transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div>
      {user && (
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">{user.email}</span>
          <button
            onClick={handleLogout}
            className="text-xs text-gray-300 hover:text-white border border-gray-600 px-3 py-1.5 rounded-lg hover:bg-gray-700 transition-colors"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  )
}