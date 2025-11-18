import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Editor from './pages/Editor'
import Mapper from './pages/Mapper'
import Converter from './pages/Converter'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="container mx-auto px-4 py-6 flex-1">
        <Routes>
          <Route path="/edit" element={<Editor />} />
          <Route path="/map" element={<Mapper />} />
          <Route path="/convert" element={<Converter />} />
          <Route path="/" element={<Navigate to="/edit" replace />} />
        </Routes>
      </main>
      <footer className="text-center py-4 text-sm text-slate-500">
        © AI Document Editor — Frontend Demo
      </footer>
    </div>
  )
}
