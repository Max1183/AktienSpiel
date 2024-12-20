import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useOutletContext } from 'react-router-dom';
import { getRequest } from '../../utils/helpers';
import Chart from 'chart.js/auto';
import * as bootstrap from 'bootstrap';
import LoadingSite from '../Loading/LoadingSite';
import WatchlistMarker from './WatchlistMarker';
import Tooltip from '../Tooltip';
import { formatCurrency } from '../../utils/helpers';
import api from '../../api';
import { useAlert } from '../Alerts/AlertProvider';

function StockDetail() {
    const { team } = useOutletContext();
    const { id } = useParams();
    const [stock, setStock] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTimeSpan, setActiveTimeSpan] = useState('Day');
    const [chart, setChart] = useState(null);

    const [buy, setBuy] = useState(true);
    const [amount, setAmount] = useState(0);

    const navigate = useNavigate();
    const { addAlert } = useAlert();

    const timeSpans = ["Day", "5 Days", "Month", "3 Months", "Year", "5 Years"];

    useEffect(() => {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

        return () => {
            tooltipList.forEach(tooltip => tooltip.dispose());
        };
    }, [stock]);

    useEffect(() => {
        getRequest(`/api/stocks/${id}/`, setIsLoading)
            .then(data => setStock(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, [id]);

    useEffect(() => {
        if (stock && stock.history_entries) {
            const chartData = stock.history_entries.find(entry => entry.name === activeTimeSpan);

            if (chartData) {
                const ctx = document.getElementById('stock-chart').getContext('2d');

                if (chart) {
                    chart.destroy();
                }

                const newChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: chartData.values.map((_, index) => index + 1),
                        datasets: [{
                            label: 'Kursverlauf',
                            data: chartData.values,
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

                setChart(newChart);
            }
        }
    }, [stock, activeTimeSpan]);

    if (isLoading) {
        return <LoadingSite />;
    }

    if (!stock) {
        return <>
            <h1>Aktie nicht gefunden!</h1>
            <p>Zurück zur <a href="/">Startseite</a></p>
        </>
    }

    const handleBuy = () => {
        setBuy(true);
    };

    const handleSell = () => {
        setBuy(false);
    };

    const handleOrder = (event) => {
        event.preventDefault();
        if (window.confirm(`Sind Sie sicher, dass Sie ${amount} Aktien ${buy ? 'kaufen' : 'verkaufen'} wollen?`)) {
            api.post('/api/transactions/', {
                stock: id,
                transaction_type: buy ? 'buy' : 'sell',
                amount: amount
            }).then(res => {
                if (res.status === 201) {
                    addAlert(`${buy ? 'Kauf' : 'Verkauf'} von ${amount} Aktien von ${stock.name} durchgeführt!`, 'success');
                    navigate('/depot');
                }
                else alert('Fehler beim erstellen des Order-Auftrags', 'danger');
            }).catch((err) => addAlert(err.message, 'danger'));
        }
    }

    const canBuy = () => {
        return parseInt(team.balance) >= stock.current_price + 15;
    }

    const canSell = () => {
        return stock.amount > 0;
    }

    const getFee = () => {
        return amount ? Math.max(15, parseInt(stock.current_price * amount * 0.001, 10)) : 0;
    }

    const getTotal = () => {
        return amount * stock.current_price + getFee() * (buy ? 1 : -1);
    }

    const getMaxAmount = () => {
        return buy ? Math.floor(team.balance / stock.current_price) : stock.amount
    }

    const isDisabled = () => {
        return amount < 1 || amount > getMaxAmount() || (buy && getTotal() > team.balance) || (!buy && amount > stock.amount);
    }

    return <div className="row">
        <div className="col-lg-6 p-2">
            <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                <div className="d-flex justify-content-between">
                    <h2>{stock.name}</h2>
                    <WatchlistMarker stock_id={stock.id} watchlist={stock.watchlist_id} />
                </div>
                <p>Ticker: {stock.ticker}</p>

                <canvas className="mb-3" id="stock-chart"></canvas>

                <div className="btn-group d-flex btn-group-sm">
                    {stock.history_entries
                        .sort((a, b) => {
                            const indexA = timeSpans.indexOf(a.name);
                            const indexB = timeSpans.indexOf(b.name);
                            return indexA - indexB;
                        }).map(entry => (
                            <button
                                type="button"
                                key={entry.id}
                                onClick={() => setActiveTimeSpan(entry.name)}
                                className={`btn btn-primary ${activeTimeSpan === entry.name ? 'active' : ''}`}
                                disabled={entry.values.length === 0}
                            >
                                {entry.name}
                            </button>
                        ))
                    }
                </div>
                <p className="mt-3 fs-4">Geldkurs: {formatCurrency(stock.current_price)}</p>
            </div>
        </div>
        <div className="col-lg-6 p-2">
            <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100 d-flex flex-column">
                <h2>Order-Formular</h2>

                <div className="row bg-info p-2 border rounded mt-1 mb-3 fs-5">
                    {buy ? (
                        <>
                            <span className='col-8'>Verfügbares Kapital:</span>
                            <span className='col-4 text-end'>{formatCurrency(team.balance)}</span>
                        </>
                    ) : (
                        <>
                            <span className='col-8'>Aktien:</span>
                            <span className='col-4 text-end'>{stock.amount}</span>
                        </>
                    )}
                </div>

                <form role="form" onSubmit={handleOrder} className="flex-grow-1 d-flex flex-column">
                    <div className="row mb-3">
                        <div className="col-sm-4 d-flex align-items-center">
                            <p className="fs-5 m-0">Orderart:</p>
                            <Tooltip text="Wähle eine Option" />
                        </div>
                        <div className="col-sm-8">
                            <button type="button" onClick={handleBuy} className={`btn btn-outline-success me-3 ${buy && 'active'} ${!canBuy() && 'disabled'}`}>Kaufen</button>
                            <button type="button" onClick={handleSell} className={`btn btn-outline-danger ${!buy && 'active'} ${!canSell() && 'disabled'}`}>Verkaufen</button>
                        </div>
                    </div>
                    <div className="row mb-3">
                        <div className="col-sm-4 d-flex align-items-center">
                            <p className="fs-5 m-0">Anzahl:</p>
                            <Tooltip text="Gib die Anzahl der Aktien ein" />
                        </div>
                        <div className="col-sm-8">
                            <input
                                className="form-control"
                                type="number"
                                value={amount}
                                placeholder="Gib die Anzahl der Aktien ein..."
                                onChange={(e) => setAmount(e.target.value)}
                                min={1}
                                max={getMaxAmount()}
                            />
                        </div>
                    </div>
                    <div className="d-flex justify-content-between align-items-center">
                        <p className="m-1 ms-0">Gebühren ca.: {formatCurrency(getFee())}</p>
                        <Tooltip text="Eine ungefähre Berechnung der Gebühren aufgrund des aktuellen Kurses" />
                    </div>
                    <div className="d-flex justify-content-between align-items-center">
                        <p className="m-1 ms-0">Gesamt ca.: {formatCurrency(getTotal())}</p>
                        <Tooltip text="Eine ungefähre Berechnung des Gesamtpreises aufgrund des aktuellen Kurses und der Orderart" />
                    </div>
                    <div className="mt-auto mt-3">
                        <button type="submit" className={`btn btn-primary mt-3 ${isDisabled() && 'disabled'}`}>Order-Auftrag erstellen</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
}

export default StockDetail;
