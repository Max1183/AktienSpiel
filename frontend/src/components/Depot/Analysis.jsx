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

        <div className="list-group mt-3">
            {analysis.map((stockHolding) => (
                <a
                    key={stockHolding.id}
                    href={`/depot/stocks/${stockHolding.id}`}
                    className={getListItemClassName(stockHolding.total_profit)}
                >
                    <div className="d-flex w-100 justify-content-between align-items-center">
                        <p className="fs-4 mb-0">{stockHolding.name}</p>
                        <p className="fs-5 mb-0">{formatCurrency(stockHolding.total_profit)}</p>
                    </div>
                </a>
            ))}
        </div>
    </div>
}

export default Analysis;
