import React from 'react';
import { useNavigate } from 'react-router-dom';

function StockDetailLink({ stock_id, color="light", children }) {
    const navigate = useNavigate();

    const handleNavigate = (e) => {
        e.preventDefault();
        navigate(`/depot/stocks/${stock_id}`);
    };

    return <>
        <button
            key={stock_id}
            type="button"
            className={`list-group-item list-group-item-action list-group-item-${color}`}
            onClick={handleNavigate}
        >
            {children}
        </button>
    </>;
};

export default StockDetailLink;
