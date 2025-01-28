import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import { AlertProvider } from './components/Alerts/AlertProvider'
import AlertList from './components/Alerts/AlertList'
import { isAdmin } from './utils/helpers';

import Login from './pages/General/Login'
import NotFound from './pages/General/NotFound'
import ProfileActivation from './pages/General/ProfileActivation'
import Admin from './pages/General/Admin'

import Start from './pages/General/Start'

import PageOutlet from './components/General/PageOutlet'
import StockHoldings from './pages/Depot/StockHoldings'
import Transactions from './pages/Depot/Transactions'
import Analysis from './pages/Depot/Analysis'
import Watchlist from './pages/Depot/Watchlist'
import DepotSearch from './pages/Depot/DepotSearch'
import StockDetail from './pages/Depot/StockDetail'

import Contest from './pages/General/Contest'

import Profile from './pages/User/Profile'
import Team from './pages/User/Team'

import Navbar from './components/Layout/Navbar'
import Footer from './components/Layout/Footer'
import BottomNavbar from './components/Layout/BottomNavbar'


function Logout() {
    localStorage.clear()
    return <Navigate to="/login" />
}

export function useWindowSize() {
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
            <PageOutlet />
        </section>
        {small ? <BottomNavbar /> : <Footer />}
    </ProtectedRoute>
}

function AdminRoute({ children }) {
    const isUserAdmin = isAdmin();
    return isUserAdmin ? <ProtectedRoute>{children}</ProtectedRoute> : <Navigate to="/" />;
}

function App() {
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
                        <Route path="analysis" element={<Analysis />} />
                        <Route path="watchlist" element={<Watchlist />} />
                        <Route path="search" element={<DepotSearch />} />
                        <Route path="stocks/:id" element={<StockDetail />} />
                    </Route>

                    <Route path="/contest" element={<ProtectedLayout />}>
                        <Route index element={<Contest />} />
                    </Route>

                    <Route path="/user" element={<ProtectedLayout />}>
                        <Route index element={<Navigate to="/user/profile" />} />
                        <Route path="profile" element={<Profile />} />
                        <Route path="team" element={<Team />} />
                    </Route>

                    <Route path="/admin" element={<AdminRoute><ProtectedLayout /></AdminRoute>}>
                        <Route index element={<Admin />} />
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
