import React from 'react';
import { useOutletContext } from 'react-router-dom';
import InfoField from '../InfoField';
import { formatCurrency } from '../../utils/helpers';
import DepotArea from './DepotArea';

function StockHoldings() {
    const { stockHoldings, loadStockHoldings } = useOutletContext();
    const { team, loadTeam } = useOutletContext();

    return <>
        <DepotArea title="Portfolio Übersicht" value={team} handleReload={loadTeam} size="6">
            {team && <div className="row row-cols-2 row-cols-md-3">
                <InfoField label="Summe Positionen" value={formatCurrency(team.portfolio_value - team.balance)} />
                <InfoField label="Barbestand" value={formatCurrency(team.balance)} />
                <InfoField label="Gesamter Depotwert" value={formatCurrency(team.portfolio_value)} />
                <InfoField label="Performance abs." value={formatCurrency(team.portfolio_value - 100000)} />
                <InfoField label="Performance %" value={(team.portfolio_value / 100000 * 100 - 100).toFixed(2) + "%"} />
                <InfoField label="Trades" value={team.trades} />
            </div>}
        </DepotArea>
        <div className="col-lg-6 p-2">
            <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                <h2>Depotverlauf</h2>
                <p>Hier kannst du den Verlauf deines Depots sehen</p>
            </div>
        </div>
        <DepotArea title="Mein Depot" value={stockHoldings} handleReload={loadStockHoldings} size="12">
            {(stockHoldings && stockHoldings.length > 0) ? <div className="list-group rounded">
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
            </div> : <div>
                <p>Du besitzt noch keine Aktien!</p>
                <p>Klicke <a href="/depot/search/">hier</a>, um nach Aktien zu suchen.</p>
            </div>}
        </DepotArea>
    </>
}

export default StockHoldings
