import React, { useState } from 'react';
import api from '../../api';

function WatchlistMarker({ stock_id, watchlist }) {
    const [watchlist_id, setWatchlistId] = useState(watchlist);

    const handleToggleWatchlist = (e) => {
        if (watchlist_id) {
            api.delete(`/api/watchlist/delete/${watchlist_id}/`).then((res) => {
                if (res.status === 204) alert('Removed stock from watchlist');
                else alert('Failed to delete watchlist');
            }).catch((err) => alert(err));
            setWatchlistId(null);
        } else {
            api.post('/api/watchlist/create/', {
                stock: stock_id
            }).then((res) => {
                if (res.status === 201) {
                    setWatchlistId(res.data.id);
                    alert('Stock added to watchlist');
                } else alert('Failed to add stock to watchlist');
            }).catch((err) => alert(err));
        }
    };

    return <button className="btn btn-sm" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Watchlist" onClick={handleToggleWatchlist}>
        <img src={`/Icons/WatchlistIcon${watchlist_id ? 'Active' : ''}.png`} alt="Watchlist" className="img-fluid" style={{ width: '30px', height: '30px' }} />
    </button>
}

export default WatchlistMarker;
