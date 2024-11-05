import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../api';
import InfoField from '../InfoField';
import LoadingSite from '../Loading/LoadingSite';

function formatNumber(number) {
    const roundedNumber = number.toFixed(2);
    const parts = roundedNumber.split('.');
    const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `${integerPart},${parts[1]}€`;
}

function StockHoldings() {
    const { team } = useOutletContext();
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
        return <LoadingSite />;
    }

    if (!stockHoldings) {
        console.log(err);
        return <>
            <h2>Fehler beim Laden der Aufträge</h2>
            {err && <p>Nachricht: {err}</p>}
        </>
    }

    return <>
        <div className="row">
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Portfolio Übersicht</h2>
                    <div className="row row-cols-2 row-cols-md-3">
                        <InfoField label="Summe Positionen" value={(team.portfolio_value - team.balance).toFixed(2) + "€"} />
                        <InfoField label="Barbestand" value={team.balance + "€"} />
                        <InfoField label="Gesamter Depotwert" value={(team.portfolio_value).toFixed(2) + "€"} />
                        <InfoField label="Performance abs." value={(team.portfolio_value - 100000).toFixed(2) + "€"} />
                        <InfoField label="Performance %" value={(team.portfolio_value / 100000 * 100 - 100).toFixed(2) + "%"} />
                        <InfoField label="Trades" value={0} />
                    </div>
                </div>
            </div>
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Depotverlauf</h2>
                    <p>Hier kannst du den Verlauf deines Depots sehen</p>
                </div>
            </div>
            <div className="col-lg-12 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Mein Depot</h2>
                    { stockHoldings.length > 0 ? <>
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
                    </> : <>
                        <p>Du besitzt noch keine Aktien!</p>
                        <p>Klicke <a href="/depot/search/">hier</a>, um nach Aktien zu suchen.</p>
                    </> }
                </div>
            </div>
        </div>
    </>
}

export default StockHoldings
