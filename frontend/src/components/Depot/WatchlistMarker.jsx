import React, { useState } from 'react';
import api from '../../api';
import { useAlert } from '../../components/Alerts/AlertProvider';

function WatchlistMarker({ stock_id, watchlist }) {
    const [watchlist_id, setWatchlistId] = useState(watchlist);
    const { addAlert } = useAlert();

    const handleToggleWatchlist = (e) => {
        if (watchlist_id) {
            api.delete(`/api/watchlist/delete/${watchlist_id}/`).then((res) => {
                if (res.status === 204) addAlert('Aktie erfolgreich von der Watchlist entfernt', 'success');
                else addAlert('Fehler beim Entfernen der Aktie von der Watchlist', 'danger');
            }).catch((err) => {
                addAlert('Fehler beim Entfernen der Aktie von der Watchlist', 'danger');
                console.log(err);
            });
            setWatchlistId(null);
        } else {
            api.post('/api/watchlist/create/', {
                stock: stock_id
            }).then((res) => {
                if (res.status === 201) {
                    setWatchlistId(res.data.id);
                    addAlert('Aktie erfolgreich zur Watchlist hinzugefügt', 'success');
                } else alert('Fehler beim Hinzufügen der Aktie zur Watchlist', 'danger');
            }).catch((err) => {
                addAlert('Fehler beim Hinzufügen der Aktie zur Watchlist', 'danger');
                console.log(err);
            });
        }
    };

    return <button className="btn btn-sm" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Watchlist" onClick={handleToggleWatchlist}>
        <img src={`/Icons/WatchlistIcon${watchlist_id ? 'Active' : ''}.png`} alt="Watchlist" className="img-fluid" style={{ width: '30px', height: '30px' }} />
    </button>
}

export default WatchlistMarker;