import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout'
import NavigationButton from '../components/NavigationButton'
import StockHoldings from '../components/Depot/StockHoldings'
import Transactions from '../components/Depot/Transactions'
import Analysis from '../components/Depot/Analysis'
import Watchlist from '../components/Depot/Watchlist'
import api from '../api';
import LoadingSite from '../components/Loading/LoadingSite';

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

    if (isLoading) return <LoadingSite />;

    if (!team) {
        console.log(err);
        return <>
            <h2>Fehler beim Laden des Depots!</h2>
            {err && <p>Nachricht: {err}</p>}
            <p>Zurück zur <a href="/">Startseite</a></p>
        </>
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
                    return <StockHoldings team={team} />
                } else if (currentSite === 'Aufträge') {
                    return <Transactions team={team} />
                } else if (currentSite === 'Auswertung') {
                    return <Analysis team={team} />
                } else if (currentSite === 'Watchlist') {
                    return <Watchlist team={team} />
                }
            })()
        }
    </Layout>
}

export default Depot
