import React, { useState, useEffect } from 'react';
import api from '../../api'
import LoadingSite from '../../components/Loading/LoadingSite';
import WatchlistItem from './WatchlistItem';

function Watchlist({ team }) {
    const [watchlist, setWatchlist] = useState([])
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);

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
            if (res.status === 204) alert('Watchlist deleted');
            else alert('Failed to delete watchlist');
            getWatchlist();
        }).catch((err) => alert(err));
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
