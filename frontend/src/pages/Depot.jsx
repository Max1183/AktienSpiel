import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout'
import NavigationButton from '../components/NavigationButton'
import StockHoldings from '../components/StockHoldings'

function Depot() {
    const [currentSite, setCurrentSite] = useState(null);

    return <Layout>
        <div className="list-group list-group-horizontal mb-3">
            <NavigationButton>Depot</NavigationButton>
            <NavigationButton>Aufträge</NavigationButton>
            <NavigationButton>Auswertung</NavigationButton>
            <NavigationButton>Watchlist</NavigationButton>
        </div>
        <StockHoldings />
    </Layout>
}

export default Depot
