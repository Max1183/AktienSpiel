import React from 'react';
import Navigation from './Navigation';
import { Safe2, Safe2Fill, CartCheck, CartCheckFill, PieChart, PieChartFill, Star, StarFill, Search } from 'react-bootstrap-icons';

const DepotNavigation = () => {
    return (
        <div className="btn-group w-100 mb-3">
            <Navigation to="/depot" name="Depot" icon={<Safe2 />} icon_active={<Safe2Fill />} />
            <Navigation to="/depot/transactions" name="Transaktionen" icon={<CartCheck />} icon_active={<CartCheckFill />} />
            <Navigation to="/depot/analysis" name="Auswertung" icon={<PieChart />} icon_active={<PieChartFill />} />
            <Navigation to="/depot/watchlist" name="Watchlist" icon={<Star />} icon_active={<StarFill />} />
            <Navigation to="/depot/search" name="Suchen" icon={<Search />} icon_active={<Search />} />
        </div>
    );
};

export default DepotNavigation;
