import React from 'react';
import WatchlistItem from './WatchlistItem';
import { useAlert } from '../Alerts/AlertProvider';
import { useOutletContext } from 'react-router-dom';
import DepotArea from './DepotArea';

function Watchlist() {
    const { watchlist, setWatchlist, loadWatchlist } = useOutletContext();
    const { addAlert } = useAlert();

    const deleteWatchlist = (e, id) => {
        e.preventDefault();
        api.delete(`/api/watchlist/delete/${id}/`).then((res) => {
            if (res.status === 204) addAlert('Watchlisteintrag erfolgreich entfernt', 'success');
            else addAlert('Fehler beim Löschen des Watchlisteintrags', 'danger');
            setWatchlist(watchlist.filter((item) => item.id !== id));
        }).catch((err) => addAlert(err.message, 'danger'));
    };

    return <>
        <DepotArea title="Watchlist" value={watchlist} handleReload={loadWatchlist}>
            {(watchlist && watchlist.length > 0) ? <>
                <p>Hier siehst du alle Aktien in deiner Watchlist.</p>
                <div className="list-group rounded mt-3">
                    {watchlist.map((list) => (
                        <WatchlistItem watchlist={list} onDelete={deleteWatchlist} key={list.id} />
                    ))}
                </div>
            </> : <>
                <p>Du hast noch keine Aktien in der Watchlist</p>
                <p>Füge Aktien hinzu, indem du auf das Sternsymbol bei der Aktie klickst.</p>
                <p>Klicke <a href="/depot/search/">hier</a>, um nach Aktien zu suchen.</p>
            </>}
        </DepotArea>
    </>
}

export default Watchlist;
