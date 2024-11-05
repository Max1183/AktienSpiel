import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function SearchBar({ oldSearchTerm }) {
    const [searchTerm, setSearchTerm] = useState(oldSearchTerm || '');
    const navigate = useNavigate();

    const handleSearch = (event) => {
        event.preventDefault();
        navigate(`/depot/search/?q=${searchTerm}`);
    };

    return (
        <form className="d-flex me-auto" role="search" onSubmit={handleSearch}>
            <input
                className="form-control me-2"
                type="search"
                placeholder="Nach Aktien suchen..."
                aria-label="Search"
                value={searchTerm}
                minLength={3}
                maxLength={100}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
        </form>
    );
}

export default SearchBar;