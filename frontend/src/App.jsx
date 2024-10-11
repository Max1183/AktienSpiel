import React from 'react'
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Register from './pages/Register'
import NotFound from './pages/NotFound'

import Start from './pages/Start'

import Depot from './pages/Depot'
import DepotSearch from './pages/DepotSearch'

import Contest from './pages/Contest'

function Logout() {
    localStorage.clear()
    return <Navigate to="/login" />
}

function RegisterAndLogout() {
    localStorage.clear()
    return <Register />
}

function Protected(Component, path) {
  return (
    <Route
      path={path}
      element={
        <ProtectedRoute>
          <Component />
        </ProtectedRoute>
      }
    />
  );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {Protected(Start, "/")}

                {Protected(Depot, "/depot")}
                {Protected(DepotSearch, "/depot/search")}

                {Protected(Contest, "/contest")}

                <Route path="/login" element={<Login />} />
                <Route path="/logout" element={<Logout />} />
                <Route path="/register" element={<RegisterAndLogout />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
