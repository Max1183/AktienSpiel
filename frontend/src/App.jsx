import React, { useState, useEffect } from 'react';
import {BrowserRouter, Routes, Route, Navigate, Outlet} from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import { AlertProvider, useAlert } from './components/Alerts/AlertProvider'
import AlertList from './components/Alerts/AlertList'

import Login from './pages/Login'
import NotFound from './pages/NotFound'
import ProfileActivation from './pages/ProfileActivation'

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

function ProtectedLayout() {
    const { width } = useWindowSize();
    const small = width < 992;

    return <ProtectedRoute>
        <Navbar small={small} />
        <section className="container mt-3">
            <AlertList />
            {location.pathname.startsWith('/depot') ? <Depot /> : <Outlet />}
        </section>
        {small ? <Navigation /> : <Footer />}
    </ProtectedRoute>
}

function App() {
    const { width } = useWindowSize();
    const small = width < 992;
    const breakpoint = 992;

    return <AlertProvider>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true, }}>
            <main className="content">
                <Routes>
                    <Route path="/" element={<ProtectedLayout />}>
                        <Route index element={<Start />} />
                    </Route>

                    <Route path="/depot" element={<ProtectedLayout />}>
                        <Route index element={<StockHoldings />} />
                        <Route path="transactions" element={<Transactions />} />
                        {/*<Route path="analysis" element={<Analysis />} />*/}
                        <Route path="watchlist" element={<Watchlist />} />
                        <Route path="search" element={<DepotSearch />} />
                        <Route path="stocks/:id" element={<StockDetail />} />
                    </Route>

                    {/*<Route path="/contest" element={<ProtectedLayout />}>
                        <Route index element={<Contest />} />
                    </Route>*/}

                    <Route path="/user" element={<ProtectedLayout />}>
                        <Route index element={<Navigate to="/user/profile" />} />
                        <Route path="profile" element={<Profile />} />
                        <Route path="team" element={<Team />} />
                    </Route>

                    <Route path="/login" element={<Login />} />
                    <Route path="/logout" element={<Logout />} />
                    <Route path="/activate/:token" element={<ProfileActivation />} />
                    <Route path="*" element={<NotFound />} />
                </Routes>
            </main>
        </BrowserRouter>
    </AlertProvider>
}

export default App
