import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { getRequest } from '../../utils/helpers';
import InfoField from '../InfoField';
import LoadingSite from '../Loading/LoadingSite';
import { formatCurrency } from '../../utils/helpers';
import { useAlert } from '../Alerts/AlertProvider';

function StockHoldings() {
    const { team } = useOutletContext();
    const [stockHoldings, setStockHoldings] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        getRequest('/api/stockholdings/', setIsLoading)
            .then(data => setStockHoldings(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, []);

    const getDepot = () => {
        if (isLoading) {
            return <LoadingSite />;
        } else if (!stockHoldings) {
            return <h2>Fehler beim Laden der Aktien!</h2>;
        } else if (stockHoldings.length > 0) {
            return <div className="list-group rounded mt-3">
                <h2>Mein Depot</h2>
                {stockHoldings.map((stockHolding) => (
                    <a key={stockHolding.id} href={`/depot/stocks/${stockHolding.stock.id}`} className="list-group-item list-group-item-action list-group-item-light">
                        <div className="d-flex w-100 justify-content-between">
                            <h5 className="mb-1">{stockHolding.stock.name}</h5>
                            <small>Kurs: {formatCurrency(stockHolding.stock.current_price)}</small>
                        </div>
                        <p className="mb-1">Anzahl: {stockHolding.amount}</p>
                        <small>Gesamtwert: {formatCurrency(stockHolding.amount * stockHolding.stock.current_price)}</small>
                    </a>
                ))}
            </div>
        } else {
            return <>
                <h2>Mein Depot</h2>
                <p>Du besitzt noch keine Aktien!</p>
                <p>Klicke <a href="/depot/search/">hier</a>, um nach Aktien zu suchen.</p>
            </>
        }
    }

    return <>
        <div className="row">
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Portfolio Übersicht</h2>
                    <div className="row row-cols-2 row-cols-md-3">
                        <InfoField label="Summe Positionen" value={formatCurrency(team.portfolio_value - team.balance)} />
                        <InfoField label="Barbestand" value={formatCurrency(team.balance)} />
                        <InfoField label="Gesamter Depotwert" value={formatCurrency(team.portfolio_value)} />
                        <InfoField label="Performance abs." value={formatCurrency(team.portfolio_value - 100000)} />
                        <InfoField label="Performance %" value={(team.portfolio_value / 100000 * 100 - 100).toFixed(2) + "%"} />
                        <InfoField label="Trades" value={team.trades} />
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
                    {getDepot()}
                </div>
            </div>
        </div>
    </>
}

export default StockHoldings
