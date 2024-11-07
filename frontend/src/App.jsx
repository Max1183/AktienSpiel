import React, { useState, useEffect } from 'react';
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Register from './pages/Register'
import NotFound from './pages/NotFound'

import Start from './pages/Start'

import Depot from './pages/Depot'
import StockHoldings from './components/Depot/StockHoldings'
import Transactions from './components/Depot/Transactions'
import Analysis from './components/Depot/Analysis'
import Watchlist from './components/Depot/Watchlist'
import DepotSearch from './components/Depot/DepotSearch'
import StockDetail from './components/Depot/StockDetail'

import Contest from './pages/Contest'

import Profile from './pages/Profile'
import Team from './pages/Team'

import Navbar from './components/Layout/Navbar'
import Footer from './components/Layout/Footer'
import Navigation from './components/Layout/Navigation'


function Logout() {
    localStorage.clear()
    return <Navigate to="/login" />
}

function RegisterAndLogout() {
    localStorage.clear()
    return <Register />
}

function Protected(Component, path) {
    return <Route
        path={path}
        element={
            <ProtectedRoute>
                <Component />
            </ProtectedRoute>
        }
    />
}

function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: undefined,
    height: undefined,
  });

  useEffect(() => {
    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

function App() {
    const { width } = useWindowSize();
    const small = width < 992;
    const breakpoint = 992;

    return <BrowserRouter future={{v7_relativeSplatPath: true,}}>
        <main className="content">
            <Navbar small={small} />
            <section className="container mt-3">

                <Routes>
                    {Protected(Start, "/")}

                    <Route path="/depot" element={<ProtectedRoute><Depot /></ProtectedRoute>}>
                        <Route index element={<StockHoldings />} />
                        <Route path="transactions" element={<Transactions />} />
                        <Route path="analysis" element={<Analysis />} />
                        <Route path="watchlist" element={<Watchlist />} />
                        <Route path="search" element={<DepotSearch />} />
                        <Route path="stocks/:id" element={<StockDetail />} />
                    </Route>

                    {Protected(Contest, "/contest")}

                    {Protected(Profile, "/user/profile")}
                    {Protected(Team, "/user/team")}

                    <Route path="/login" element={<Login />} />
                    <Route path="/logout" element={<Logout />} />
                    <Route path="/register" element={<RegisterAndLogout />} />
                    <Route path="*" element={<NotFound />} />
                </Routes>

            </section>
            {small ? <Navigation /> : <Footer />}
        </main>
    </BrowserRouter>
}

export default App
