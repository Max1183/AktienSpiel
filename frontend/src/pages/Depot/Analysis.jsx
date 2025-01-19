import React from 'react';
import { formatCurrency } from '../../utils/helpers';
import { useOutletContext } from 'react-router-dom';
import Area from '../../components/General/Area';
import DepotNavigation from '../../components/Navigation/DepotNavigation';
import StockDetailLink from '../../components/Depot/StockDetailLink';


function Analysis() {
    const { getData } = useOutletContext();

    const getColor = (total_profit) => {
        return total_profit > 0 ? 'success' : (total_profit < 0 ? (total_profit < -200 ? 'danger' : 'warning') : 'secondary');
    };

    return <>
        <DepotNavigation />
        <Area title="Auswertung" key1="analysis" size="12">
            {(getData("analysis") && getData("analysis").length > 0) ? <>
                <p>Hier siehst du, wie viel Gewinn bzw. Verlust deine Aktien gemacht haben und wie viel du davon jeweils besitzt.</p>
                <div className="list-group mt-3">
                    {getData("analysis").map((stockHolding) => (
                        <StockDetailLink stock_id={stockHolding.id} color={getColor(stockHolding.total_profit)}>
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
                        </StockDetailLink>
                    ))}
                </div>
            </> : <>
                <p>Du besitzt noch keine Aktien.</p>
            </>}
        </Area>
    </>
}

export default Analysis;
