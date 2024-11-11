import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate, NavLink } from 'react-router-dom';
import LoadingSite from '../components/Loading/LoadingSite';
import NavigationButton from '../components/NavigationButton'
import api from '../api';

function Depot() {
    const location = useLocation();
    const navigate = useNavigate();
    const [team, setTeam] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);

    useEffect(() => {
        const getTeam = async () => {
            try {
                const response = await api.get(`/api/team/`);
                setTeam(response.data)
            } catch (error) {
                setErr(error.message);
            } finally {
                setIsLoading(false);
            }
        };

        getTeam();
    }, []);

    if (isLoading) return <LoadingSite />;

    if (!team) {
        console.log(err);
        return <>
            <h2>Fehler beim Laden des Depots!</h2>
            {err && <p>Nachricht: {err}</p>}
            <p>Zurück zur <a href="/">Startseite</a></p>
        </>
    }

    const handleNavigation = (path) => {
        navigate(path);
    };

    const getClassName = (isActive) => {
        return `list-group-item list-group-item-action list-group-item-primary text-center p-2 ${isActive ? 'active' : ''}`;
    };

    return <>
        <div className="list-group list-group-horizontal mb-3">
            <NavLink to="/depot" end className={({ isActive }) => getClassName(isActive)}>Depot</NavLink>
            <NavLink to="/depot/transactions" className={({ isActive }) => getClassName(isActive)}>Aufträge</NavLink>
            <NavLink to="/depot/analysis" className={({ isActive }) => getClassName(isActive)}>Auswertung</NavLink>
            <NavLink to="/depot/watchlist" className={({ isActive }) => getClassName(isActive)}>Watchlist</NavLink>
            <NavLink to="/depot/search" className={({ isActive }) => getClassName(isActive)}>Suchen</NavLink>
        </div>
        <Outlet context={{team: team}} />
    </>;
}

export default Depot
