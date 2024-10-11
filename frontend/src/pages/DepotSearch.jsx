import React, { useState, useEffect } from 'react';
import api from '../api';
import { useSearchParams } from 'react-router-dom';
import Layout from '../components/Layout';
import SearchBar from '../components/SearchBar';

function DepotSearch() {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q') || '';
    const [searchResults, setSearchResults] = useState([]);

    useEffect(() => {
        const getSearchResults = async () => {
            try {
                const res = await api.get(`/api/search/?q=${query}`);
                setSearchResults(res.data);
            } catch (err) {
                alert(err); // Oder eine bessere Fehlerbehandlung
                console.error("Fehler bei der Suche:", err); // Fehler im Log ausgeben
            }
        };

        if (query) {
            getSearchResults();
        } else {
            setSearchResults([]);
        }
    }, [query]);

    return <Layout>
        <h1>Suchen</h1>
        <SearchBar oldSearchTerm={query} />
        <p>{searchResults.length} Ergebnisse für "{query}"</p>
        {searchResults.map((result) => (
            <div key={result.id}>{result.name} - {result.current_price}€</div>
        ))}
    </Layout>
}

export default DepotSearch;
