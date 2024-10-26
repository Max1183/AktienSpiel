import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout'
import NavigationButton from '../components/NavigationButton'
import StockHoldings from '../components/StockHoldings'

function Depot() {
    const [currentSite, setCurrentSite] = useState('Depot');
    const [team, setTeam] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);

    useEffect(() => {
        const getTeam = async () => {
            try {
                const response = await api.get(`/api/team/`);
                setTeam(response.data)
                setErr(null);
            } catch (error) {
                setErr(error.message);
            } finally {
                setIsLoading(false);
            }
        };

        getTeam();
    }, []);

    if (isLoading) {
        return <>
            <p>Lädt...</p>
        </>;
    }

    const handleDepot = () => {
        setCurrentSite('Depot');
    }

    const handleAuftrag = () => {
        setCurrentSite('Aufträge');
    }

    const handleAuswertung = () => {
        setCurrentSite('Auswertung');
    }

    const handleWatchlist = () => {
        setCurrentSite('Watchlist');
    }

    return <Layout>
        <div className="list-group list-group-horizontal mb-3">
            <NavigationButton onclick={handleDepot} active={currentSite}>Depot</NavigationButton>
            <NavigationButton onclick={handleAuftrag} active={currentSite}>Aufträge</NavigationButton>
            <NavigationButton onclick={handleAuswertung} active={currentSite}>Auswertung</NavigationButton>
            <NavigationButton onclick={handleWatchlist} active={currentSite}>Watchlist</NavigationButton>
        </div>
        {
            (() => {
                if (currentSite === 'Depot') {
                    return <StockHoldings />
                } else if (currentSite === 'Aufträge') {
                    return <div>Aufträge</div>
                } else if (currentSite === 'Auswertung') {
                    return <div>Auswertung</div>
                } else if (currentSite === 'Watchlist') {
                    return <div>Watchlist</div>
                }
            })()
        }
    </Layout>
}

export default Depot
