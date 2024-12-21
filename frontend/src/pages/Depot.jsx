import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAlert } from '../components/Alerts/AlertProvider';
import { getRequest } from '../utils/helpers';
import { Safe2, Safe2Fill, CartCheck, CartCheckFill, PieChart, PieChartFill, Star, StarFill, Search } from 'react-bootstrap-icons';
import DepotNavigation from '../components/Depot/DepotNavigation';

function Depot() {
    const { addAlert } = useAlert();

    const [team, setTeam] = useState(null);
    const [stockHoldings, setStockHoldings] = useState(null);
    const [transactions, setTransactions] = useState(null);
    const [analysis, setAnalysis] = useState(null);

    const loadTeam = (setIsLoading) => {
        getRequest('/api/team/', setIsLoading)
            .then(data => setTeam(data))
            .catch(error => addAlert(error.message, 'danger'));
    }

    const loadStockHoldings = (setIsLoading) => {
        getRequest('/api/stockholdings/', setIsLoading)
            .then(data => setStockHoldings(data))
            .catch(error => addAlert(error.message, 'danger'));
    }

    const loadTransactions = (setIsLoading) => {
        getRequest('/api/transactions/', setIsLoading)
            .then(data => setTransactions(data))
            .catch(error => addAlert(error.message, 'danger'));
    }

    const loadAnalysis = (setIsLoading) => {
        getRequest('/api/analysis/', setIsLoading)
            .then(data => setAnalysis(data))
            .catch(error => addAlert(error.message, 'danger'));
    }

    return <>
        <div className="btn-group w-100 mb-3">
            <DepotNavigation to="/depot" name="Depot" icon={<Safe2 />} icon_active={<Safe2Fill />} />
            <DepotNavigation to="/depot/transactions" name="Transaktionen" icon={<CartCheck />} icon_active={<CartCheckFill />} />
            <DepotNavigation to="/depot/analysis" name="Auswertung" icon={<PieChart />} icon_active={<PieChartFill />} />
            <DepotNavigation to="/depot/watchlist" name="Watchlist" icon={<Star />} icon_active={<StarFill />} />
            <DepotNavigation to="/depot/search" name="Suchen" icon={<Search />} icon_active={<Search />} />
        </div>
        <div className="row">
            <Outlet context={{
                team: team,
                loadTeam: loadTeam,
                stockHoldings: stockHoldings,
                loadStockHoldings: loadStockHoldings,
                transactions: transactions,
                loadTransactions: loadTransactions,
                analysis: analysis,
                loadAnalysis, loadAnalysis,
            }} />
        </div>
    </>;
}

export default Depot
