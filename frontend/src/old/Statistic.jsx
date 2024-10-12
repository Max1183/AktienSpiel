import React from "react";
import "../styles/Statistic.css"

function Statistic({ statistic, onDelete }) {
    const formattedDate = new Date(statistic.date).toLocaleDateString("de-DE")

    return (
        <div className="statistic-container">
            <p className="statistic-title">{statistic.name}</p>
            <p className="statistic-content">{statistic.description}</p>
            <p className="statistic-date">{formattedDate}</p>
            <button className="delete-button" onClick={() => onDelete(statistic.id)}>
                Delete
            </button>
        </div>
    );
}

export default Statistic
