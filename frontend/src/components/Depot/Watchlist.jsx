import React from 'react';
import WatchlistItem from './WatchlistItem';
import { useAlert } from '../Alerts/AlertProvider';
import { useOutletContext } from 'react-router-dom';
import DepotArea from './DepotArea';
import api from '../../api';

function Watchlist() {
    const { getData, loadValue } = useOutletContext();
    const { addAlert } = useAlert();

    const deleteWatchlist = (e, id) => {
        e.preventDefault();
        api.delete(`/api/watchlist/${id}/delete/`).then((res) => {
            if (res.status === 204) addAlert('Watchlisteintrag erfolgreich entfernt', 'success');
            else addAlert('Fehler beim Löschen des Watchlisteintrags', 'danger');
            loadValue('watchlist')
        }).catch((err) => addAlert(err.message, 'danger'));
    };

    return <>
        <DepotArea title="Watchlist" key1="watchlist">
            {(getData("watchlist") && getData("watchlist").length > 0) ? <>
                <p>Hier siehst du alle Aktien in deiner Watchlist.</p>
                <div className="list-group rounded mt-3">
                    {getData("watchlist").map((watchlistItem) => (
                        <WatchlistItem watchlist={watchlistItem} onDelete={deleteWatchlist} key={watchlistItem.id} />
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
