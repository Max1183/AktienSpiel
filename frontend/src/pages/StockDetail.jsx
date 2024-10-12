import Layout from '../components/Layout'
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import Chart from 'chart.js/auto';

function StockDetail() {
    const { id } = useParams();
    const [stock, setStock] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);
    const [activeTimeSpan, setActiveTimeSpan] = useState('1 Year');
    const [chart, setChart] = useState(null);

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
        return <Layout>
            <p>Lädt...</p>
        </Layout>;
    }

    if (!stock) {
        return <Layout>
            <h1>Aktie nicht gefunden!</h1>
            {err && <p>Nachricht: {err}</p>}
            <p>Zurück zur <a href="/">Startseite</a></p>
        </Layout>
    }

    return <Layout>
        <h1>{stock.name}</h1>
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
        <div className="d-flex justify-content-around">
            <button type="button" className="btn btn-success" onClick={() => alert('Aktie gekauft!')}>Kaufen</button>
            <button type="button" className="btn btn-danger" onClick={() => alert('Aktie verkauft!')}>Verkaufen</button>
        </div>
    </Layout>
}

export default StockDetail
