import React, { useState, useEffect } from 'react';
import { getRequest } from '../../utils/helpers';
import LoadingSite from '../../components/Loading/LoadingSite';
import WatchlistItem from './WatchlistItem';
import api from '../../api';
import { useAlert } from '../../components/Alerts/AlertProvider';

function Watchlist({ team }) {
    const [watchlist, setWatchlist] = useState([])
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        getRequest('/api/watchlist/', setIsLoading)
            .then(data => setWatchlist(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, []);

    if (isLoading) return <LoadingSite />;

    if (!watchlist) return <h2>Fehler beim Laden der Watchlist!</h2>;

    const deleteWatchlist = (e, id) => {
        e.preventDefault();
        api.delete(`/api/watchlist/delete/${id}/`).then((res) => {
            if (res.status === 204) addAlert('Watchlisteintrag erfolgreich entfernt', 'success');
            else addAlert('Fehler beim Löschen des Watchlisteintrags', 'danger');
            setWatchlist(watchlist.filter((item) => item.id !== id));
        }).catch((err) => addAlert(err.message, 'danger'));
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
