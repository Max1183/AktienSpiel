import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate, NavLink } from 'react-router-dom';
import LoadingSite from '../components/Loading/LoadingSite';
import { useAlert } from '../components/Alerts/AlertProvider';
import { getRequest } from '../utils/helpers';

function Depot() {
    const location = useLocation();
    const navigate = useNavigate();
    const [team, setTeam] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        getRequest('/api/team/', setIsLoading)
            .then(data => setTeam(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, []);

    if (isLoading) return <LoadingSite />;

    const handleNavigation = (path) => {
        navigate(path);
    };

    const getClassName = (isActive) => {
        return `list-group-item list-group-item-action list-group-item-primary text-center p-2 ${isActive ? 'active' : ''}`;
    };

    return <>
        <div className="list-group list-group-horizontal mb-3">
            <NavLink to="/depot" end className={({ isActive }) => getClassName(isActive)}>Depot</NavLink>
            <NavLink to="/depot/transactions" className={({ isActive }) => getClassName(isActive)}>Transaktionen</NavLink>
            {/*<NavLink to="/depot/analysis" className={({ isActive }) => getClassName(isActive)}>Auswertung</NavLink>*/}
            <NavLink to="/depot/watchlist" className={({ isActive }) => getClassName(isActive)}>Watchlist</NavLink>
            <NavLink to="/depot/search" className={({ isActive }) => getClassName(isActive)}>Suchen</NavLink>
        </div>
        {!team ?
            <h2>Fehler beim Laden des Depots!</h2> :
            <Outlet context={{team: team}} />
        }
    </>;
}

export default Depot
