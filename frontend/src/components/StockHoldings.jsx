import React, { useEffect, useState } from 'react';
import api from '../api';

function formatNumber(number) {
  const roundedNumber = number.toFixed(2);
  const parts = roundedNumber.split('.');
  const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${integerPart},${parts[1]}€`;
}

function StockHoldings() {
    const [stockHoldings, setStockHoldings] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);

    useEffect(() => {
        const getStockHoldings = async () => {
            try {
                const response = await api.get(`/api/stockholdings/`);
                setStockHoldings(response.data)
                setErr(null);
            } catch (error) {
                setErr(error.message);
            } finally {
                setIsLoading(false);
            }
        };

        getStockHoldings();
    }, []);

    if (isLoading) {
        return <>
            <p>Lädt...</p>
        </>;
    }

    if (!stockHoldings) {
        console.log(err);
        return <>
            <h2>Fehler beim Laden des Depots!</h2>
            {err && <p>Nachricht: {err}</p>}
            <p>Zurück zur <a href="/">Startseite</a></p>
        </>
    }

    return <>
        <h2 className="mb-0">Mein Depot</h2>
        <small className="text-end">Deine Notizen zu den Orders findest du unter "Aufträge"</small>
        <div className="list-group rounded mt-3">
            {stockHoldings.map((stockHolding) => (
                <a key={stockHolding.id} href={`/depot/stocks/${stockHolding.stock.id}`} className="list-group-item list-group-item-action list-group-item-light">
                    <div className="d-flex w-100 justify-content-between">
                        <h5 className="mb-1">{stockHolding.stock.name}</h5>
                        <small>Kurs: {stockHolding.stock.current_price}€</small>
                    </div>
                    <p className="mb-1">Anzahl: {stockHolding.amount}</p>
                    <small>Gesamtwert: {formatNumber(stockHolding.amount * stockHolding.stock.current_price)}</small>
                </a>
            ))}
        </div>
    </>
}

export default StockHoldings
