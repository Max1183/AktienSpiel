import React, { useEffect, useState, useRef } from 'react';
import { useOutletContext } from 'react-router-dom';
import InfoField from '../../components/General/InfoField';
import { formatCurrency } from '../../utils/helpers';
import Area from '../../components/General/Area';
import Chart from 'chart.js/auto';
import DepotNavigation from '../../components/Navigation/DepotNavigation';
import StockDetailLink from '../../components/Depot/StockDetailLink';

function StockHoldings() {
    const { getData } = useOutletContext();
    const chartRef = useRef(null);

    useEffect(() => {
        const teamData = getData("team");
        if (teamData && teamData.portfolio_history.length >= 3) {
            const chartData = teamData.portfolio_history;

            if (chartData) {
                const chart = document.getElementById('portfolio-chart');
                if (!chart) {
                    return;
                }

                const ctx = chart.getContext('2d');


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
        <DepotNavigation />
        <Area title="Portfolio Übersicht" key1="team" size="6">
            {({ value: team }) => <div className='row g-2 m-0'>
                <InfoField label="Summe Positionen" value={formatCurrency(team.portfolio_value - team.balance)} />
                <InfoField label="Barbestand" value={formatCurrency(team.balance)} />
                <InfoField label="Gesamter Depotwert" value={formatCurrency(team.portfolio_value)} />
                <InfoField label="Performance abs." value={formatCurrency(team.portfolio_value - 100000)} />
                <InfoField label="Performance %" value={(team.portfolio_value / 100000 * 100 - 100).toFixed(2) + "%"} />
                <InfoField label="Trades" value={team.trades} />
            </div>}
        </Area>
        <Area title="Depotverlauf" size="6">
            {({ value: team }) => team && team.portfolio_history.length >= 3 ? (
                <canvas className="mb-3" id="portfolio-chart"></canvas>
            ) : <p>Hier kannst du den Verlauf deines Depots sehen</p>}
        </Area>
        <Area title="Mein Depot" key1="stockholdings">
            {({ value: stockholdings }) => stockholdings.length > 0 ? (
                <div className="list-group rounded">
                    {stockholdings.map((stockHolding) => (
                        <StockDetailLink stock_id={stockHolding.stock.id}>
                            <div className="d-flex w-100 justify-content-between">
                                <h5 className="mb-1">{stockHolding.stock.name}</h5>
                                <small>Kurs: {formatCurrency(stockHolding.stock.current_price)}</small>
                            </div>
                            <p className="mb-1">Anzahl: {stockHolding.amount}</p>
                            <small>Gesamtwert: {formatCurrency(stockHolding.amount * stockHolding.stock.current_price)}</small>
                        </StockDetailLink>
                    ))}
                </div>
            ) : <div>
                <p>Du besitzt noch keine Aktien!</p>
                <p>Klicke <a href="/depot/search/">hier</a>, um nach Aktien zu suchen.</p>
            </div>}
        </Area>
    </>
}

export default StockHoldings
