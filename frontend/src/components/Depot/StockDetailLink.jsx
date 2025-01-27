import React from "react";
import { useNavigate } from "react-router-dom";

function StockDetailLink({ stock_id, color = "light", children }) {
    const navigate = useNavigate();

    const handleNavigate = (e) => {
        e.preventDefault();
        navigate(`/depot/stocks/${stock_id}`);
    };

    return (
        <>
            <a
                href="#"
                key={stock_id + Math.random()}
                className={`list-group-item list-group-item-action list-group-item-${color}`}
                onClick={handleNavigate}
            >
                {children}
            </a>
        </>
    );
}

export default StockDetailLink;
