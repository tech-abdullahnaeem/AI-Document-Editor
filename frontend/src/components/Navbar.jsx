import React from 'react'
import { NavLink } from 'react-router-dom'

const Link = ({ to, children }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `px-3 py-2 rounded-md ${isActive ? 'bg-primary-600 text-white' : 'text-slate-700 hover:bg-primary-50'}`
    }
  >
    {children}
  </NavLink>
)

export default function Navbar() {
  return (
    <nav className="bg-white border-b">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-xl font-semibold text-primary-600">AI Doc Editor</div>
          <div className="flex items-center space-x-2">
            <Link to="/edit">AI Editor</Link>
            <Link to="/map">Format Mapper</Link>
            <Link to="/convert">PDF → LaTeX</Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
