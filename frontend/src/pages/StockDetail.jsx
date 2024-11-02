import Layout from '../components/Layout/Layout'
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import Chart from 'chart.js/auto';
import * as bootstrap from 'bootstrap';
import LoadingSite from '../components/Loading/LoadingSite';


function StockDetail() {
    const { id } = useParams();
    const [stock, setStock] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);
    const [activeTimeSpan, setActiveTimeSpan] = useState('Year');
    const [chart, setChart] = useState(null);

    const [buy, setBuy] = useState(true);
    const [amount, setAmount] = useState(0);

    const navigate = useNavigate();

    useEffect(() => {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

        return () => {
            tooltipList.forEach(tooltip => tooltip.dispose());
        };
    }, [stock]);

    useEffect(() => {
        const fetchStock = async () => {
            try {
                const response = await api.get(`/api/stocks/${id}/`);
                setStock(response.data)
                setErr(null);
            } catch (error) {
                setErr(error.message);
                console.log(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchStock();
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
        return <Layout>
            <h1>Aktie nicht gefunden!</h1>
            {err && <p>Nachricht: {err}</p>}
            <p>Zurück zur <a href="/">Startseite</a></p>
        </Layout>
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
                    alert(`${buy ? 'Kauf' : 'Verkauf'} von ${amount} Aktien von ${stock.name} durchgeführt!`);
                    navigate('/depot');
                }
                else alert('Fehler beim erstellen des Order-Auftrags');
            }).catch((err) => console.log(err));
        }
    }

    return <Layout>
        <div className="row">
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>{stock.name}</h2>
                    <p>Ticker: {stock.ticker}</p>

                    <canvas className="mb-3" id="stock-chart"></canvas>

                    <div className="btn-group d-flex btn-group-sm">
                        {stock.history_entries.sort((a, b) => a.id - b.id).map(entry => (
                            <button
                                type="button"
                                key={entry.id}
                                onClick={() => setActiveTimeSpan(entry.name)}
                                className={`btn btn-primary ${activeTimeSpan === entry.name ? 'active' : ''}`}
                                disabled={entry.values.length === 0}
                            >
                                {entry.name}
                            </button>
                        ))}
                    </div>
                    <p className="mt-3 fs-4">Geldkurs: {stock.current_price}</p>
                </div>
            </div>
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100 d-flex flex-column">
                    <h2>Order-Formular</h2>

                    <div className="row bg-info p-2 border rounded mt-1 mb-3 fs-5">
                        {buy ? (
                            <>
                                <span className='col-8'>Verfügbares Kapital:</span>
                                <span className='col-4 text-end'>0€</span>
                            </>
                        ) : (
                            <>
                                <span className='col-8'>Aktien:</span>
                                <span className='col-4 text-end'>0</span>
                            </>
                        )}
                    </div>

                    <form role="form" onSubmit={handleOrder} className="flex-grow-1 d-flex flex-column">
                        <div className="row">
                            <div className="col-sm-4">
                                <p className="fs-5 mb-1">
                                    Orderart: <img
                                        width="15"
                                        height="15"
                                        src="/Tooltip.png"
                                        data-bs-toggle="tooltip"
                                        data-bs-placement="top"
                                        data-bs-title="Wähle eine Option" />
                                </p>
                            </div>
                            <div className="col-sm-8 mb-3">
                                <button type="button" onClick={handleBuy} className={`btn btn-outline-success me-3 ${buy && 'active'}`}>Kaufen</button>
                                <button type="button" onClick={handleSell} className={`btn btn-outline-danger ${!buy && 'active'}`}>Verkaufen</button>
                            </div>
                        </div>
                        <div className="row mb-2">
                            <div className="col-sm-4">
                                <p className="fs-5 mb-1">Anzahl:</p>
                            </div>
                            <div className="col-sm-8 mb-3">
                                <input
                                    className="form-control"
                                    type="number"
                                    value={amount}
                                    placeholder="Gib die Anzahl der Aktien ein..."
                                    onChange={(e) => setAmount(e.target.value)}
                                    min={1}
                                    max={100}
                                />
                            </div>
                        </div>
                        <p>Gebühren ca.: 0.00 €</p>
                        <p className="m-0">Gesamt ca.: 0.00 €</p>
                        <div className="mt-auto mt-3">
                            <button type="submit" className="btn btn-primary mt-3">Order-Auftrag erstellen</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </Layout>
}

export default StockDetail;
