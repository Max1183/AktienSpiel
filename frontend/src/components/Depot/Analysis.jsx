import React from 'react';
import { formatCurrency } from '../../utils/helpers';
import { useOutletContext } from 'react-router-dom';
import DepotArea from './DepotArea';


function Analysis() {
    const { getData } = useOutletContext();

    const getListItemClassName = (total_profit) => {
        const color = total_profit > 0 ? 'success' : (total_profit < 0 ? (total_profit < -200 ? 'danger' : 'warning') : 'secondary');
        return `list-group-item list-group-item-action list-group-item-${color}`;
    };

    return <>
        <DepotArea title="Auswertung" key1="analysis" size="12">
            {(getData("analysis") && getData("analysis").length > 0) ? <>
                <p>Hier siehst du, wie viel Gewinn bzw. Verlust deine Aktien gemacht haben und wie viel du davon jeweils besitzt.</p>
                <div className="list-group mt-3">
                    {getData("analysis").map((stockHolding) => (
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
            </> : <>
                <p className="text-center">Keine Aktien gefunden.</p>
            </>}
        </DepotArea>
    </>
}

export default Analysis;
