import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate, NavLink } from 'react-router-dom';
import LoadingSite from '../components/Loading/LoadingSite';
import { useAlert } from '../components/Alerts/AlertProvider';
import { getRequest } from '../utils/helpers';
import { Safe2, Safe2Fill, CartCheck, CartCheckFill, PieChart, PieChartFill, Star, StarFill, Search, ArrowClockwise } from 'react-bootstrap-icons';
import DepotNavigation from '../components/Depot/DepotNavigation';

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

    return <>
        <div className="btn-group w-100 mb-3">
            <DepotNavigation to="/depot" name="Depot" icon={<Safe2 />} icon_active={<Safe2Fill />} />
            <DepotNavigation to="/depot/transactions" name="Transaktionen" icon={<CartCheck />} icon_active={<CartCheckFill />} />
            <DepotNavigation to="/depot/analysis" name="Auswertung" icon={<PieChart />} icon_active={<PieChartFill />} />
            <DepotNavigation to="/depot/watchlist" name="Watchlist" icon={<Star />} icon_active={<StarFill />} />
            <DepotNavigation to="/depot/search" name="Suchen" icon={<Search />} icon_active={<Search />} />
        </div>
        {!team ?
            <h2>Fehler beim Laden des Depots!</h2> :
            <Outlet context={{team: team}} />
        }
    </>;
}

export default Depot
