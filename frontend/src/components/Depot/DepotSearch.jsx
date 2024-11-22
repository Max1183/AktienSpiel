import React, { useState, useEffect } from 'react';
import { getRequest } from '../../utils/helpers';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../SearchBar';
import { formatCurrency } from '../../utils/helpers';
import { useAlert } from '../Alerts/AlertProvider';
import LoadingSite from '../Loading/LoadingSite';

function DepotSearch() {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q') || '';
    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const { addAlert } = useAlert();

    useEffect(() => {
        if (!query || query.length < 3) {
            setSearchResults([]);
            return;
        }

        getRequest(`/api/search/?q=${query}`, setIsLoading)
            .then(data => setSearchResults(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, [query]);

    return <div className="bg-primary-subtle p-3 shadow rounded">
        <h1>Suchen</h1>
        <SearchBar oldSearchTerm={query} />
        <p>
            {query ? (
                `${searchResults.length} Ergebnisse für "${query}".`
            ) : (
                "Geben Sie einen Suchbegriff ein."
            )}
        </p>
        <div className="mb-3">
            {isLoading && <LoadingSite />}
        </div>
        <div className="list-group">
            {searchResults.map((stock) => (
                <a key={stock.id} href={'/depot/stocks/' + stock.id} className="list-group-item list-group-item-action">
                    <div className="d-flex w-100 justify-content-between">
                        <p className="mb-0">{stock.name}</p>
                        <p className="mb-0">{formatCurrency(stock.current_price)}</p>
                    </div>
                </a>
            ))}
        </div>
    </div>
}

export default DepotSearch;
