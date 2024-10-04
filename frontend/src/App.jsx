import React from 'react'
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Register from './pages/Register'
import NotFound from './pages/NotFound'

import Home from './pages/Home'
import About from './pages/About'
import Contact from './pages/Contact'
import CreateStatistic from './pages/CreateStatistic'
import Statistics from './pages/Statistics'

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
                {Protected(Home, "/")}
                {Protected(About, "/about")}
                {Protected(Contact, "/contact")}
                {Protected(CreateStatistic, "/statistics/create")}
                {Protected(Statistics, "/statistics/view")}
                <Route path="/login" element={<Login />} />
                <Route path="/logout" element={<Logout />} />
                <Route path="/register" element={<RegisterAndLogout />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
