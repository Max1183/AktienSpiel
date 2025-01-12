import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, useOutletContext } from 'react-router-dom';
import Chart from 'chart.js/auto';
import * as bootstrap from 'bootstrap';
import LoadingSite from '../Loading/LoadingSite';
import WatchlistMarker from './WatchlistMarker';
import Tooltip from '../Tooltip';
import { formatCurrency } from '../../utils/helpers';
import api from '../../api';
import { useAlert } from '../Alerts/AlertProvider';
import DepotArea from './DepotArea';

function StockDetail() {
    const { id } = useParams();
    const { getData, loadValue } = useOutletContext();
    const [isLoading, setIsLoading] = useState(false);
    const [activeTimeSpan, setActiveTimeSpan] = useState('Day');
    const [buy, setBuy] = useState(true);
    const [amount, setAmount] = useState(0);
    const navigate = useNavigate();
    const { addAlert } = useAlert();
    const timeSpans = ["Day", "5 Days", "Month", "3 Months", "Year", "5 Years"];
    const chartRef = useRef(null);

    useEffect(() => {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

        return () => {
            tooltipList.forEach(tooltip => tooltip.dispose());
             if (chartRef.current) {
                    chartRef.current.destroy();
                }
        };
    }, []);

    useEffect(() => {
        const stock = getData('stocks') && getData('stocks')[id]
        if (document.getElementById('stock-chart') && stock && stock.history_entries) {
            const chartData = stock.history_entries.find(entry => entry.name === activeTimeSpan);

            if (chartData) {
                const ctx = document.getElementById('stock-chart').getContext('2d');

                if (chartRef.current) {
                    chartRef.current.destroy();
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
                 chartRef.current = newChart;
            }
        }
     }, [getData, id, activeTimeSpan]);

    const handleBuy = () => {
        setBuy(true);
    };

    const handleSell = () => {
        setBuy(false);
    };

    const handleOrder = async (event) => {
        event.preventDefault();
        if (window.confirm(`Sind Sie sicher, dass Sie ${amount} Aktien ${buy ? 'kaufen' : 'verkaufen'} wollen?`)) {
            setIsLoading(true);
            try {
                   const res = await api.post('/api/transactions/create/', {
                        stock: id,
                        transaction_type: buy ? 'buy' : 'sell',
                        amount: amount
                    });
                    if (res.status === 201) {
                         addAlert(`${buy ? 'Kauf' : 'Verkauf'} von ${amount} Aktien von ${getData('stocks')[id].name} durchgeführt!`, 'success');
                         navigate('/depot');
                   }
                   else addAlert('Fehler beim erstellen des Order-Auftrags', 'danger');
                } catch (err) {
                   addAlert(err.message, 'danger')
                }
                setIsLoading(false);
        }
        setIsLoading(false);
    }

    const getTitle = () => {
        return getData('stocks') && getData('stocks')[id] ? getData('stocks')[id].name : "Aktie";
    }

    const canBuy = () => {
        const team = getData('team');
        const stock = getData('stocks') && getData('stocks')[id]
        return team && stock && parseInt(team.balance) >= stock.current_price + 15;
    }

    const canSell = () => {
        const stock = getData('stocks') && getData('stocks')[id]
        return stock && stock.amount > 0;
    }

    const getFee = () => {
        const stock = getData('stocks') && getData('stocks')[id]
        return stock && amount ? Math.max(15, parseInt(stock.current_price * amount * 0.001, 10)) : 0;
    }


    const getTotal = () => {
        const stock = getData('stocks') && getData('stocks')[id]
        return stock && amount ? amount * stock.current_price + getFee() * (buy ? 1 : -1) : 0;
    }


    const getMaxAmount = () => {
        const team = getData('team');
        const stock = getData('stocks') && getData('stocks')[id]
        return buy && team && stock ? Math.floor(team.balance / stock.current_price) : stock ? stock.amount : 0
    }

    const isDisabled = () => {
        const stock = getData('stocks') && getData('stocks')[id];
        const team = getData('team');
        return !stock || !team || amount < 1 || amount > getMaxAmount() || (buy && getTotal() > team.balance) || (!buy && amount > stock.amount);
    }

    return !isLoading ? <>
        <DepotArea title={getTitle()} key1="stocks" handleReload={() => loadValue('stocks', id)} size="6" reloadButton={true}>
            {getData('stocks') && getData('stocks')[id] && <>
                <p>Ticker: {getData('stocks')[id].ticker}</p>
                <canvas className="mb-3" id="stock-chart"></canvas>

                <div className="btn-group d-flex btn-group-sm">
                    {getData('stocks')[id].history_entries
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
                <div className='mt-3 d-flex justify-content-between'>
                    <p className="fs-4 mb-0 mt-auto">Geldkurs: {formatCurrency(getData('stocks')[id].current_price)}</p>
                    <WatchlistMarker stock_id={id} watchlist={getData('stocks')[id].watchlist_id}/>
                </div>
            </>}
        </DepotArea>
        <DepotArea title="Order-Formular" key1="team" size="6" reloadButton={false}>
            {(getData('team') &&  getData('stocks') &&  getData('stocks')[id]) ? <>
               <div className="row bg-info p-2 border rounded mt-1 mb-3 fs-5">
                    {buy ? (
                        <>
                            <span className='col-8'>Verfügbares Kapital:</span>
                            <span className='col-4 text-end'>{formatCurrency(getData('team').balance)}</span>
                        </>
                    ) : (
                        <>
                            <span className='col-8'>Aktien:</span>
                            <span className='col-4 text-end'>{getData('stocks')[id].amount}</span>
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
                    <div className="mt-2">
                        <button type="submit" className={`btn btn-primary mt-3 ${isDisabled() && 'disabled'}`}>Order-Auftrag erstellen</button>
                    </div>
                </form>
            </> : <LoadingSite />}
        </DepotArea>
    </> : <LoadingSite />
}

export default StockDetail;
