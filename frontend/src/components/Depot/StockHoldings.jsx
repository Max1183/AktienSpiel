import React, { useEffect, useState, useRef } from 'react';
import { useOutletContext } from 'react-router-dom';
import InfoField from '../InfoField';
import { formatCurrency } from '../../utils/helpers';
import DepotArea from './DepotArea';
import Chart from 'chart.js/auto';

function StockHoldings() {
    const { getData } = useOutletContext();
    const chartRef = useRef(null);

    useEffect(() => {
        const teamData = getData("team");
        if (teamData && teamData.portfolio_history.length >= 3) {
            const chartData = teamData.portfolio_history;

            if (chartData) {
                const ctx = document.getElementById('portfolio-chart').getContext('2d');


                if (chartRef.current) {
                    chartRef.current.destroy();
                }

                 const newChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: chartData.map((_, index) => index + 1),
                        datasets: [{
                            label: 'Depotverlauf',
                            data: chartData,
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: false
                            }
                        }
                    }
                });
                 chartRef.current = newChart;
            }
        }
        return () => {
          if(chartRef.current) chartRef.current.destroy();
        }
    }, [getData("team")]);

    return <>
        <DepotArea title="Portfolio Übersicht" key1="team" size="6">
            {getData("team") && <div className="row row-cols-2 row-cols-md-3">
                <InfoField label="Summe Positionen" value={formatCurrency(getData("team").portfolio_value - getData("team").balance)} />
                <InfoField label="Barbestand" value={formatCurrency(getData("team").balance)} />
                <InfoField label="Gesamter Depotwert" value={formatCurrency(getData("team").portfolio_value)} />
                <InfoField label="Performance abs." value={formatCurrency(getData("team").portfolio_value - 100000)} />
                <InfoField label="Performance %" value={(getData("team").portfolio_value / 100000 * 100 - 100).toFixed(2) + "%"} />
                <InfoField label="Trades" value={getData("team").trades} />
            </div>}
        </DepotArea>
        <div className="col-lg-6 p-2">
            <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                <h2>Depotverlauf</h2>
                {(getData("team") && getData("team").portfolio_history.length >= 3) ? (
                    <canvas className="mb-3" id="portfolio-chart"></canvas>
                ) : <p>Hier kannst du den Verlauf deines Depots sehen</p>}
            </div>
        </div>
        <DepotArea title="Mein Depot" key1="stockholdings">
            {(getData("stockholdings") && getData("stockholdings").length > 0) ? <div className="list-group rounded">
                {getData("stockholdings").map((stockHolding) => (
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
