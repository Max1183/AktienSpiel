import React, { useState, useEffect } from 'react';
import api from '../../api';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../SearchBar';

function DepotSearch() {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q') || '';
    const [searchResults, setSearchResults] = useState([]);

    useEffect(() => {
        const getSearchResults = async () => {
            if (query.length < 3) {
                setSearchResults([]);
                return;
            }

            try {
                const res = await api.get(`/api/search/?q=${query}`);
                setSearchResults(res.data);
            } catch (err) {
                alert(err);
                console.error("Fehler bei der Suche:", err);
            }
        };

        if (query) {
            getSearchResults();
        } else {
            setSearchResults([]);
        }
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
        <div className="list-group">
            {searchResults.map((stock) => (
                <a key={stock.id} href={'/depot/stocks/' + stock.id} className="list-group-item list-group-item-action">
                    {stock.name} - {stock.current_price}€
                </a>
            ))}
        </div>
    </div>
}

export default DepotSearch;
