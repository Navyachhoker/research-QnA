// src/components/Navbar.jsx

import { NavLink } from "react-router-dom";

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
  return (
    <nav className="bg-slate-900 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-8 py-4">

        <h1 className="text-xl font-bold text-indigo-400">
          ResearchGPT
        </h1>

        <div className="flex gap-4">

          {navLinks.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              end
              className={({ isActive }) =>
                `px-4 py-2 rounded-lg transition-all duration-200 ${
                  isActive
                    ? "bg-indigo-600 text-white"
                    : "text-gray-300 hover:bg-slate-800 hover:text-white"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}

        </div>
      </div>
    </nav>
  );
}