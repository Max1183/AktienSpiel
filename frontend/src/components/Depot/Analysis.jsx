import React, { useEffect } from 'react';
import { getRequest, formatCurrency } from '../../utils/helpers';
import { useAlert } from '../Alerts/AlertProvider';
import LoadingSite from '../Loading/LoadingSite';


function Analysis({ team }) {
    const [analysis, setAnalysis] = React.useState(null);
    const [isLoading, setIsLoading] = React.useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        getRequest(`/api/analysis/`, setIsLoading)
            .then(data => setAnalysis(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, []);

    const getListItemClassName = (total_profit) => {
        const color = total_profit > 0 ? 'success' : (total_profit < 0 ? (total_profit < -200 ? 'danger' : 'warning') : 'secondary');
        return `list-group-item list-group-item-action list-group-item-${color}`;
    };

    if (isLoading) return <LoadingSite />;

    return <div className="bg-primary-subtle p-3 shadow rounded p-3">
        <h2 className="mb-0">Auswertung</h2>
        <small>Hier siehst du, wie sich der Wert deiner Aktien seit Kauf verändert hat!</small>

        {analysis.length === 0 ? (
            <p className="text-center">Keine Aktien gefunden.</p>
        ) : (
            <div className="list-group mt-3">
                {analysis.map((stockHolding) => (
                    <a
                        key={stockHolding.id}
                        href={`/depot/stocks/${stockHolding.id}`}
                        className={getListItemClassName(stockHolding.total_profit)}
                    >
                        <div className="d-flex w-100 justify-content-between align-items-center">
                            <p className="fs-5 mb-0">{stockHolding.name}</p>
                            <div className="d-flex flex-column align-items-end">
                                <p className="mb-0 fs-6">
                                    {formatCurrency(stockHolding.total_profit)}
                                </p>
                                {stockHolding.current_holding != 0 && (
                                    <p className="fs-6 mb-0">
                                        {formatCurrency(stockHolding.current_holding)}
                                    </p>
                                )}
                            </div>
                        </div>
                    </a>
                ))}
            </div>
        )}
    </div>
}

export default Analysis;
