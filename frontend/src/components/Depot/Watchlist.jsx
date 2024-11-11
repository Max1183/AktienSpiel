import React, { useState, useEffect } from 'react';
import api from '../../api'
import LoadingSite from '../../components/Loading/LoadingSite';
import WatchlistItem from './WatchlistItem';
import { useAlert } from '../../components/Alerts/AlertProvider';

function Watchlist({ team }) {
    const [watchlist, setWatchlist] = useState([])
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);
    const { addAlert } = useAlert();

    const getWatchlist = async () => {
        try {
            const response = await api.get(`/api/watchlist/`);
            setWatchlist(response.data)
        } catch (error) {
            setErr(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        getWatchlist();
    }, []);

    if (isLoading) return <LoadingSite />;

    if (!watchlist) {
        addAlert('Fehler beim Laden der Watchliste', 'danger');
        console.log(err);
        return <>
            <h2>Fehler beim Laden des Depots!</h2>
            {err && <p>Nachricht: {err}</p>}
            <p>Zurück zur <a href="/">Startseite</a></p>
        </>
    }

    const deleteWatchlist = (e, id) => {
        e.preventDefault();
        api.delete(`/api/watchlist/delete/${id}/`).then((res) => {
            if (res.status === 204) addAlert('Watchlisteintrag erfolgreich entfernt', 'success');
            else addAlert('Fehler beim Löschen des Watchlisteintrags', 'danger');
            getWatchlist();
        }).catch((err) => addAlert(err, 'danger'));
    };

    return <div className="bg-primary-subtle p-3 shadow rounded p-3">
        <h2 className="mb-0">Watchlist</h2>
        {watchlist.length === 0 ? (
            <>
                <p>Du hast noch keine Aktien in der Watchlist</p>
                <p>Klicke <a href="/depot/search/">hier</a>, um nach Aktien zu suchen.</p>
            </>
        ) : (
            <div className="list-group rounded mt-3">
                {watchlist.map((list) => (
                    <WatchlistItem watchlist={list} onDelete={deleteWatchlist} key={list.id} />
                ))}
            </div>
        )}
    </div>
}

export default Watchlist;
