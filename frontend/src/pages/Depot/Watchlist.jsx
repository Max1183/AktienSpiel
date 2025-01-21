import React from 'react';
import WatchlistItem from '../../components/Depot/WatchlistItem';
import { useAlert } from '../../components/Alerts/AlertProvider';
import { useOutletContext } from 'react-router-dom';
import Area from '../../components/General/Area';
import api from '../../api';
import DepotNavigation from '../../components/Navigation/DepotNavigation';

function Watchlist() {
    const { loadValue, changeLoading } = useOutletContext();
    const { addAlert } = useAlert();

    const deleteWatchlist = (e, id) => {
        e.preventDefault();
        changeLoading("watchlist", true);
        api.delete(`/api/watchlist/${id}/delete/`).then((res) => {
            if (res.status === 204) addAlert('Watchlisteintrag erfolgreich entfernt', 'success');
            else addAlert('Fehler beim Löschen des Watchlisteintrags', 'danger');
            loadValue('watchlist')
        }).catch((err) => addAlert(err.message, 'danger'))
    };

    return <>
        <DepotNavigation />
        <Area title="Watchlist" key1="watchlist">
            {({ value: watchlist }) => watchlist.length > 0 ? <>
                <p>Hier siehst du alle Aktien in deiner Watchlist.</p>
                <div className="list-group rounded mt-3">
                    {watchlist.map((watchlistItem) => (
                        <WatchlistItem watchlist={watchlistItem} onDelete={deleteWatchlist} key={watchlistItem.id} />
                    ))}
                </div>
            </> : <>
                <p>Du hast noch keine Aktien in der Watchlist</p>
                <p>Füge Aktien hinzu, indem du auf das Sternsymbol bei der Aktie klickst.</p>
            </>}
        </Area>
    </>
}

export default Watchlist;
